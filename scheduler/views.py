from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from functools import wraps
from datetime import date, datetime

from .forms import (
    CustomerRegistrationForm,
    AppointmentForm,
    ContactForm,
    ReviewForm,
    CustomerProfileForm,
)
from .models import Service, Appointment, CustomerProfile, Gadget, Review, ContactMessage


def is_admin(user):
    return user.is_staff


def admin_required(view_func):
    """Only staff accounts may reach the view. Anonymous users are sent to
    login; authenticated customers get a clear 403 instead of being bounced
    in a redirect loop back to the login page."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if not request.user.is_staff:
            raise PermissionDenied("This area is reserved for DC Gadgets staff accounts.")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    services = Service.objects.filter(is_active=True)
    popular_services = services.filter(is_popular=True)[:4]
    gadgets = Gadget.objects.filter(in_stock=True)[:6]
    reviews = Review.objects.filter(is_featured=True)[:3]
    
    # Simple estimate calculator presets
    device_categories = [
        ("iphone", "iPhone / Smartphone"),
        ("macbook", "MacBook / Laptop"),
        ("pc", "Custom Desktop PC"),
        ("console", "PS5 / Xbox / Switch"),
    ]

    contact_form = ContactForm()

    context = {
        "services": services,
        "popular_services": popular_services,
        "gadgets": gadgets,
        "reviews": reviews,
        "device_categories": device_categories,
        "contact_form": contact_form,
        "total_repairs_count": 1480 + Appointment.objects.filter(status="COMPLETED").count(),
    }
    return render(request, "scheduler/home.html", context)


def services_catalog(request):
    category_filter = request.GET.get("category")
    search_query = request.GET.get("q")

    services = Service.objects.filter(is_active=True)
    if category_filter:
        services = services.filter(category=category_filter)
    if search_query:
        services = services.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    categories = Service.CATEGORY_CHOICES
    return render(
        request,
        "scheduler/services_catalog.html",
        {
            "services": services,
            "categories": categories,
            "selected_category": category_filter,
            "search_query": search_query,
        },
    )


def store_catalog(request):
    category_filter = request.GET.get("category")
    brand_filter = request.GET.get("brand")
    search_query = request.GET.get("q")

    gadgets = Gadget.objects.all()
    if category_filter:
        gadgets = gadgets.filter(category=category_filter)
    if brand_filter:
        gadgets = gadgets.filter(brand__iexact=brand_filter)
    if search_query:
        gadgets = gadgets.filter(Q(name__icontains=search_query) | Q(brand__icontains=search_query) | Q(specs__icontains=search_query))

    categories = Gadget.CATEGORY_CHOICES
    brands = Gadget.objects.values_list("brand", flat=True).distinct()

    return render(
        request,
        "scheduler/store_catalog.html",
        {
            "gadgets": gadgets,
            "categories": categories,
            "brands": brands,
            "selected_category": category_filter,
            "selected_brand": brand_filter,
            "search_query": search_query,
        },
    )


@login_required
def book_appointment(request):
    profile, _ = CustomerProfile.objects.get_or_create(
        user=request.user, defaults={"phone_number": "", "address": ""}
    )
    
    initial_data = {}
    service_id = request.GET.get("service_id")
    if service_id:
        initial_data["service"] = service_id
    if profile.preferred_device:
        initial_data["device_model"] = profile.preferred_device

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = profile
            appointment.full_clean()
            appointment.save()
            messages.success(
                request,
                f"Appointment booked! Your Tracking Code is {appointment.tracking_code}.",
            )
            return redirect("my_appointments")
    else:
        form = AppointmentForm(initial=initial_data)

    services = Service.objects.filter(is_active=True)
    return render(request, "scheduler/book_appointment.html", {"form": form, "services": services})


def track_repair(request):
    code = request.GET.get("code", "").strip()
    appointment = None
    searched = False
    if code:
        searched = True
        appointment = Appointment.objects.filter(
            Q(tracking_code__iexact=code) | Q(customer__phone_number__contains=code)
        ).first()

    return render(request, "scheduler/track_repair.html", {"appointment": appointment, "code": code, "searched": searched})


@login_required
def my_appointments(request):
    profile = get_object_or_404(CustomerProfile, user=request.user)
    appointments = profile.appointments.all().select_related("service")
    review_form = ReviewForm()
    return render(
        request,
        "scheduler/my_appointments.html",
        {"appointments": appointments, "profile": profile, "review_form": review_form},
    )


@login_required
def customer_profile_view(request):
    profile = get_object_or_404(CustomerProfile, user=request.user)
    if request.method == "POST":
        p_form = CustomerProfileForm(request.POST, instance=profile)
        if p_form.is_valid():
            p_form.save()
            request.user.first_name = p_form.cleaned_data["first_name"]
            request.user.last_name = p_form.cleaned_data["last_name"]
            request.user.email = p_form.cleaned_data["email"]
            request.user.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("customer_profile")
    else:
        p_form = CustomerProfileForm(
            instance=profile,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
        )
    return render(request, "scheduler/profile.html", {"form": p_form, "profile": profile})


@login_required
def cancel_appointment(request, pk):
    profile = get_object_or_404(CustomerProfile, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, customer=profile)
    if appointment.status in ["PENDING", "CONFIRMED"]:
        appointment.status = "CANCELLED"
        appointment.save()
        messages.info(request, f"Appointment {appointment.tracking_code} has been cancelled.")
    else:
        messages.error(request, "Cannot cancel an appointment that is already in progress or completed.")
    return redirect("my_appointments")


@login_required
def submit_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for submitting your review!")
    return redirect("my_appointments")


def submit_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! We have received your message and will respond shortly.")
        else:
            messages.error(request, "Please check the form for errors.")
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            profile = form.save()
            login(request, profile.user)
            messages.success(request, f"Welcome to DC Gadgets, {profile.user.first_name or profile.user.username}!")
            return redirect("book_appointment")
    else:
        form = CustomerRegistrationForm()
    return render(request, "scheduler/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("admin_dashboard" if user.is_staff else "my_appointments")
        messages.error(request, "Invalid username or password. Please try again.")
    return render(request, "scheduler/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@admin_required
def admin_dashboard(request):
    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")

    appointments = Appointment.objects.select_related("customer__user", "service").all()
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if search_query:
        appointments = appointments.filter(
            Q(tracking_code__icontains=search_query)
            | Q(customer__user__username__icontains=search_query)
            | Q(device_model__icontains=search_query)
        )

    # Metrics
    total_count = Appointment.objects.count()
    pending_count = Appointment.objects.filter(status="PENDING").count()
    in_progress_count = Appointment.objects.filter(status="IN_PROGRESS").count()
    ready_count = Appointment.objects.filter(status="READY").count()
    completed_count = Appointment.objects.filter(status="COMPLETED").count()
    
    total_est_revenue = Appointment.objects.filter(
        status__in=["CONFIRMED", "IN_PROGRESS", "READY", "COMPLETED"]
    ).aggregate(Sum("service__price"))["service__price__sum"] or 0

    unread_messages = ContactMessage.objects.filter(is_read=False)

    context = {
        "appointments": appointments,
        "status_filter": status_filter,
        "search_query": search_query,
        "metrics": {
            "total": total_count,
            "pending": pending_count,
            "in_progress": in_progress_count,
            "ready": ready_count,
            "completed": completed_count,
            "revenue": total_est_revenue,
        },
        "unread_messages": unread_messages,
        "statuses": Appointment.STATUS_CHOICES,
    }
    return render(request, "scheduler/admin_dashboard.html", context)


@admin_required
def update_status(request, pk):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get("status")
        admin_notes = request.POST.get("admin_notes", "")
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            if admin_notes:
                appointment.admin_notes = admin_notes
            appointment.save()
            messages.success(request, f"Updated {appointment.tracking_code} status to {appointment.get_status_display()}.")
    return redirect("admin_dashboard")


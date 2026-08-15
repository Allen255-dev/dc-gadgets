from django.contrib import admin
from .models import Service, CustomerProfile, Appointment, Gadget, Review, ContactMessage


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "duration_minutes", "price", "is_popular", "is_active")
    list_filter = ("category", "is_active", "is_popular")
    search_fields = ("name", "description")


@admin.register(Gadget)
class GadgetAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "badge", "in_stock", "rating")
    list_filter = ("category", "brand", "in_stock")
    search_fields = ("name", "brand", "specs")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "preferred_device", "created_at")
    search_fields = ("user__username", "user__first_name", "phone_number")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "customer", "service", "device_model", "appointment_date", "appointment_time", "status")
    list_filter = ("status", "service", "appointment_date")
    list_editable = ("status",)
    search_fields = ("tracking_code", "customer__user__username", "device_model")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "service", "is_featured", "created_at")
    list_filter = ("rating", "is_featured")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")


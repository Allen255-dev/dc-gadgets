from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import secrets


class Service(models.Model):
    """A bookable service offered by the gadget store."""

    CATEGORY_CHOICES = [
        ("REPAIR", "Hardware Repair"),
        ("CONSULTATION", "Tech Consultation"),
        ("DEMO", "Product Demo & Setup"),
        ("DIAGNOSTICS", "Diagnostic Check"),
        ("UPGRADE", "Hardware Upgrade & Custom PC"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="REPAIR")
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    icon = models.CharField(max_length=50, default="wrench", help_text="Lucide/FontAwesome icon name")
    warranty_info = models.CharField(max_length=100, default="90-Day Warranty included", blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} (₦{self.price})"


class Gadget(models.Model):
    """Product showcase catalog for DC Gadgets store."""

    CATEGORY_CHOICES = [
        ("SMARTPHONE", "Smartphones & Tablets"),
        ("LAPTOP", "Laptops & Computers"),
        ("GAMING", "Gaming Consoles & Gear"),
        ("AUDIO", "Audio & Wearables"),
        ("ACCESSORY", "Accessories & Cables"),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    original_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    badge = models.CharField(max_length=30, blank=True, help_text="e.g. Hot, Refurbished, Best Seller, New")
    specs = models.CharField(max_length=255, blank=True, help_text="Short bullet points separated by comma")
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    in_stock = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.name}"


class CustomerProfile(models.Model):
    """Extends Django's built-in User with store-specific customer data."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    preferred_device = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    """A scheduled booking linking a customer to a service at a specific time."""

    STATUS_CHOICES = [
        ("PENDING", "Pending Approval"),
        ("CONFIRMED", "Confirmed & Scheduled"),
        ("IN_PROGRESS", "Repair / Service In Progress"),
        ("READY", "Ready for Pickup"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    tracking_code = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    device_model = models.CharField(max_length=100, default="General Device", help_text="e.g. iPhone 14 Pro, Dell XPS 15")
    issue_description = models.TextField(blank=True, help_text="Describe the issue or request")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    estimated_completion = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Customer notes")
    admin_notes = models.TextField(blank=True, help_text="Internal tech notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-appointment_date", "-appointment_time"]

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"DC-{secrets.token_hex(3).upper()}"
        super().save(*args, **kwargs)

    def clean(self):
        # Business rule: cannot book in the past
        if self.appointment_date and self.appointment_time:
            naive_dt = datetime.combine(self.appointment_date, self.appointment_time)
            if naive_dt < datetime.now() and not self.pk:
                raise ValidationError("Cannot book an appointment in the past.")

    def end_time(self):
        start = datetime.combine(self.appointment_date, self.appointment_time)
        return (start + timedelta(minutes=self.service.duration_minutes)).time()

    def __str__(self):
        return f"[{self.tracking_code}] {self.customer} - {self.service} on {self.appointment_date}"


class Review(models.Model):
    """Customer testimonials and ratings for services."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.rating} Stars"


class ContactMessage(models.Model):
    """Messages submitted via the contact form."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


from django import forms
from django.contrib.auth.models import User
from .models import Appointment, CustomerProfile, ContactMessage, Review, Service


class CustomerRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"placeholder": "Choose a username", "class": "input-field"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "your.email@example.com", "class": "input-field"}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "First Name", "class": "input-field"}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "Last Name", "class": "input-field"}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"placeholder": "+234 801 234 5678", "class": "input-field"}))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"placeholder": "Street Address, City", "class": "input-field"}))
    preferred_device = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"placeholder": "e.g. iPhone 15 Pro, Gaming PC", "class": "input-field"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Secure Password", "class": "input-field"}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken. Please choose another.")
        return username

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password"],
        )
        return CustomerProfile.objects.create(
            user=user,
            phone_number=data["phone_number"],
            address=data["address"],
            preferred_device=data.get("preferred_device", ""),
        )


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["service", "device_model", "issue_description", "appointment_date", "appointment_time", "notes"]
        widgets = {
            "service": forms.Select(attrs={"class": "input-field"}),
            "device_model": forms.TextInput(attrs={"placeholder": "e.g. iPhone 14 Pro, Dell XPS 15, PS5", "class": "input-field"}),
            "issue_description": forms.Textarea(attrs={"rows": 3, "placeholder": "Describe what is wrong or what service you need (e.g. cracked screen, liquid spill, slow boot)", "class": "input-field"}),
            "appointment_date": forms.DateInput(attrs={"type": "date", "class": "input-field"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time", "class": "input-field"}),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Any special preferences or technician instructions?", "class": "input-field"}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("appointment_date")
        time = cleaned.get("appointment_time")
        if date and time:
            clash = Appointment.objects.filter(
                appointment_date=date,
                appointment_time=time,
                status__in=["PENDING", "CONFIRMED", "IN_PROGRESS"],
            )
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError("That exact date and time slot is currently booked. Please select another time.")
        return cleaned


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your Full Name", "class": "input-field"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com", "class": "input-field"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone Number (Optional)", "class": "input-field"}),
            "subject": forms.TextInput(attrs={"placeholder": "How can we help?", "class": "input-field"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Enter your message or inquiry...", "class": "input-field"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "service", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} Stars {'★'*i}") for i in range(5, 0, -1)], attrs={"class": "input-field"}),
            "service": forms.Select(attrs={"class": "input-field"}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your experience with DC Gadgets...", "class": "input-field"}),
        }


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "input-field"}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "input-field"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "input-field"}))

    class Meta:
        model = CustomerProfile
        fields = ["phone_number", "address", "preferred_device"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "input-field"}),
            "address": forms.TextInput(attrs={"class": "input-field"}),
            "preferred_device": forms.TextInput(attrs={"class": "input-field"}),
        }


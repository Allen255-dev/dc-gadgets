from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_catalog, name="services_catalog"),
    path("store/", views.store_catalog, name="store_catalog"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("track/", views.track_repair, name="track_repair"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("profile/", views.customer_profile_view, name="customer_profile"),
    path("cancel/<int:pk>/", views.cancel_appointment, name="cancel_appointment"),
    path("review/", views.submit_review, name="submit_review"),
    path("contact/", views.submit_contact, name="submit_contact"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/appointment/<int:pk>/status/", views.update_status, name="update_status"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]


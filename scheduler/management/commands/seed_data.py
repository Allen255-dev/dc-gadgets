from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scheduler.models import Service, Gadget, CustomerProfile, Appointment, Review
from datetime import date, time, timedelta


class Command(BaseCommand):
    help = "Seeds database with realistic initial data for DC Gadgets store."

    def handle(self, *args, **options):
        self.stdout.write("Seeding data for DC Gadgets...")

        # 1. Services
        services_data = [
            {
                "name": "iPhone Screen & Battery Express Replacement",
                "category": "REPAIR",
                "description": "Premium OEM-grade OLED screen and high-capacity battery installation with true-tone programming.",
                "duration_minutes": 45,
                "price": 89.00,
                "icon": "smartphone",
                "warranty_info": "90-Day Hassle-Free Warranty",
                "is_popular": True,
            },
            {
                "name": "Laptop Liquid & Logic Board Diagnostics",
                "category": "DIAGNOSTICS",
                "description": "Full teardown, ultrasonic logic board cleaning, chip-level diagnosis, and detailed repair cost estimate.",
                "duration_minutes": 60,
                "price": 49.00,
                "icon": "laptop-diagnostic",
                "warranty_info": "Diagnostic fee credited toward repair",
                "is_popular": False,
            },
            {
                "name": "Custom Gaming PC Assembly & Tuning",
                "category": "UPGRADE",
                "description": "Professional component installation, ultra-clean cable routing, BIOS optimization, and 24-hour stress testing.",
                "duration_minutes": 120,
                "price": 129.00,
                "icon": "cpu",
                "warranty_info": "1-Year Build Craftsmanship Guarantee",
                "is_popular": True,
            },
            {
                "name": "MacBook Thermal Cleaning & Paste Service",
                "category": "REPAIR",
                "description": "Deep internal dust removal, fan lubrication, and premium liquid-metal / Arctic thermal paste re-application.",
                "duration_minutes": 45,
                "price": 69.00,
                "icon": "fan",
                "warranty_info": "6-Month Cooling Guarantee",
                "is_popular": False,
            },
            {
                "name": "Console HDMI Port & Motherboard Repair",
                "category": "REPAIR",
                "description": "Micro-soldering replacement for damaged HDMI 2.1 ports on PS5, Xbox Series X, or Nintendo Switch.",
                "duration_minutes": 60,
                "price": 95.00,
                "icon": "gamepad-2",
                "warranty_info": "90-Day Warranty included",
                "is_popular": True,
            },
            {
                "name": "SSD High-Speed Storage & RAM Upgrade",
                "category": "UPGRADE",
                "description": "NVMe M.2 SSD installation, 1:1 drive cloning, and RAM expansion for PCs & MacBooks.",
                "duration_minutes": 30,
                "price": 55.00,
                "icon": "hard-drive",
                "warranty_info": "Lifetime Installation Warranty",
                "is_popular": True,
            },
            {
                "name": "Audio Gear & Hi-Fi DAC Setup Demo",
                "category": "DEMO",
                "description": "Test high-end audiophile headphones, DAC amplifiers, and spatial audio in our acoustic demo booth.",
                "duration_minutes": 30,
                "price": 0.00,
                "icon": "headphones",
                "warranty_info": "Complimentary In-Store Experience",
                "is_popular": False,
            },
            {
                "name": "Smart Home & Ecosystem Consultation",
                "category": "CONSULTATION",
                "description": "Personalized 1-on-1 consultation to design your home automation, mesh Wi-Fi, and smart security setup.",
                "duration_minutes": 45,
                "price": 39.00,
                "icon": "home-wifi",
                "warranty_info": "Includes custom diagram & gear list",
                "is_popular": False,
            },
        ]

        for s_data in services_data:
            Service.objects.get_or_create(name=s_data["name"], defaults=s_data)

        self.stdout.write(f"Services seeded: {Service.objects.count()}")

        # 2. Gadgets Showcase Catalog
        gadgets_data = [
            {
                "name": "iPhone 15 Pro Max 256GB - Natural Titanium",
                "category": "SMARTPHONE",
                "brand": "Apple",
                "price": 949.00,
                "original_price": 1199.00,
                "badge": "Best Seller",
                "specs": "A17 Pro Chip, 48MP Camera, USB-C, 99% Battery Health",
                "description": "Refurbished Grade A+ in mint condition with original box and 1-year store warranty.",
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80",
                "rating": 4.9,
            },
            {
                "name": "MacBook Air 15-inch M2 (16GB RAM / 512GB SSD)",
                "category": "LAPTOP",
                "brand": "Apple",
                "price": 1099.00,
                "original_price": 1399.00,
                "badge": "Refurbished",
                "specs": "Apple M2 8-core CPU, 10-core GPU, Liquid Retina Display, Midnight",
                "description": "Ultralight power laptop tested and certified by DC Gadgets tech team.",
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
                "rating": 5.0,
            },
            {
                "name": "PlayStation 5 Slim Digital Edition 1TB",
                "category": "GAMING",
                "brand": "Sony",
                "price": 449.00,
                "original_price": 499.00,
                "badge": "Hot",
                "specs": "1TB Custom High-Speed SSD, 4K 120Hz Output, DualSense Wireless Controller",
                "description": "Brand new sealed box with official Sony manufacturer warranty.",
                "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop&q=80",
                "rating": 4.8,
            },
            {
                "name": "Sony WH-1000XM5 Noise-Canceling Headphones",
                "category": "AUDIO",
                "brand": "Sony",
                "price": 329.00,
                "original_price": 399.00,
                "badge": "Top Rated",
                "specs": "Industry-leading ANC, 30-hour battery life, Speak-to-Chat, Silver",
                "description": "Exceptional clarity and bass response for studio and daily listening.",
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
                "rating": 4.9,
            },
            {
                "name": "ASUS ROG Ally Z1 Extreme Gaming Handheld",
                "category": "GAMING",
                "brand": "ASUS",
                "price": 599.00,
                "original_price": 699.00,
                "badge": "New Arrival",
                "specs": "AMD Z1 Extreme, 120Hz FHD Display, 16GB LPDDR5, Windows 11",
                "description": "Play all your PC games anywhere. Pre-tested and thermal calibrated.",
                "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
                "rating": 4.7,
            },
            {
                "name": "Anker 737 Power Bank (PowerCore 24K 140W)",
                "category": "ACCESSORY",
                "brand": "Anker",
                "price": 99.00,
                "original_price": 149.00,
                "badge": "Essential",
                "specs": "24,000mAh Capacity, 140W Ultra-Fast Charging, Smart Digital Display",
                "description": "Powers laptops, MacBooks, and smartphones multiple times over.",
                "image_url": "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=600&auto=format&fit=crop&q=80",
                "rating": 4.9,
            },
        ]

        for g_data in gadgets_data:
            Gadget.objects.get_or_create(name=g_data["name"], defaults=g_data)

        self.stdout.write(f"Gadgets seeded: {Gadget.objects.count()}")

        # 3. Customer Users & Sample Appointments
        user1, created = User.objects.get_or_create(
            username="john_doe",
            defaults={
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        if created:
            user1.set_password("password123")
            user1.save()

        prof1, _ = CustomerProfile.objects.get_or_create(
            user=user1,
            defaults={"phone_number": "+1 (555) 234-5678", "address": "742 Evergreen Terrace, Tech City", "preferred_device": "iPhone 14 Pro & MacBook Pro"},
        )

        user2, created2 = User.objects.get_or_create(
            username="sarah_connor",
            defaults={
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "last_name": "Connor",
            },
        )
        if created2:
            user2.set_password("password123")
            user2.save()

        prof2, _ = CustomerProfile.objects.get_or_create(
            user=user2,
            defaults={"phone_number": "+1 (555) 987-6543", "address": "101 Cyberdyne Way, Tech Valley", "preferred_device": "Custom Gaming PC"},
        )

        # Sample Appointments
        screen_service = Service.objects.filter(category="REPAIR").first()
        pc_service = Service.objects.filter(category="UPGRADE").first()

        if screen_service and not Appointment.objects.filter(customer=prof1).exists():
            today = date.today()
            Appointment.objects.create(
                customer=prof1,
                service=screen_service,
                device_model="iPhone 14 Pro Max",
                issue_description="Cracked glass screen after drop. Touch screen still responsive.",
                appointment_date=today + timedelta(days=1),
                appointment_time=time(14, 0),
                status="CONFIRMED",
                notes="Prefers afternoon appointment.",
            )

        if pc_service and not Appointment.objects.filter(customer=prof2).exists():
            today = date.today()
            Appointment.objects.create(
                customer=prof2,
                service=pc_service,
                device_model="Custom RTX 4080 Build",
                issue_description="Need new AIO liquid cooler installed and cable management.",
                appointment_date=today + timedelta(days=2),
                appointment_time=time(11, 30),
                status="PENDING",
                notes="Brought my own Lian Li fans.",
            )

        self.stdout.write(f"Appointments seeded: {Appointment.objects.count()}")

        # 4. Reviews
        reviews_data = [
            {
                "user": user1,
                "rating": 5,
                "comment": "DC Gadgets revived my water-damaged MacBook in under 24 hours! Saved all my work files. Honest tech team and super clean shop.",
                "is_featured": True,
            },
            {
                "user": user2,
                "rating": 5,
                "comment": "The custom PC build service is top notch. Cable management looks like a work of art and thermal performance is unreal!",
                "is_featured": True,
            },
        ]
        for r_data in reviews_data:
            Review.objects.get_or_create(user=r_data["user"], comment=r_data["comment"], defaults=r_data)

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with full DC Gadgets data!"))

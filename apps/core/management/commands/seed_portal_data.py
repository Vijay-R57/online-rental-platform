import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser, TenantDocument
from apps.properties.models import Property, PropertyImage, Amenity
from apps.rentals.models import RentalApplication, Booking, Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest


class Command(BaseCommand):
    help = "Populate the database with realistic demo data for presentation and grading."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Online Property Rental Portal database...")

        # 1. Amenities
        amenities_data = [
            ("High-Speed Wi-Fi", "bi-wifi"),
            ("Dedicated Parking Space", "bi-car-front"),
            ("Central Air Conditioning", "bi-snow"),
            ("In-Unit Washer & Dryer", "bi-water"),
            ("Swimming Pool", "bi-water"),
            ("Fitness Gym", "bi-heart-pulse"),
            ("Private Balcony", "bi-door-open"),
            ("Modern Dishwasher", "bi-cup-hot"),
            ("Pet Friendly", "bi-paw"),
            ("24/7 Security & Access Control", "bi-shield-check"),
            ("Passenger Elevator", "bi-arrow-down-up"),
        ]
        amenity_objs = {}
        for name, icon in amenities_data:
            obj, _ = Amenity.objects.get_or_create(name=name, defaults={'icon_class': icon})
            amenity_objs[name] = obj

        # 2. Users
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@rentease.local',
                'role': CustomUser.Role.ADMIN,
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('AdminPass123!')
            admin_user.save()

        owner_john, _ = CustomUser.objects.get_or_create(
            username='landlord_john',
            defaults={
                'email': 'john.owner@rentease.local',
                'role': CustomUser.Role.OWNER,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+1 (555) 234-5678',
                'is_verified': True,
                'address': '742 Evergreen Terrace',
                'city': 'Metro City',
                'state': 'CA',
                'postal_code': '94105',
                'occupation': 'Real Estate Investor',
                'company_name': 'Apex Residential Holdings',
                'bio': 'Experienced property landlord with over 10 years of providing premier housing.'
            }
        )
        if not owner_john.has_usable_password():
            owner_john.set_password('OwnerPass123!')
            owner_john.save()

        owner_sarah, _ = CustomUser.objects.get_or_create(
            username='landlord_sarah',
            defaults={
                'email': 'sarah.owner@rentease.local',
                'role': CustomUser.Role.OWNER,
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'phone_number': '+1 (555) 345-6789',
                'is_verified': True,
                'city': 'Austin',
                'state': 'TX',
                'occupation': 'Property Manager',
                'company_name': 'Lone Star Living'
            }
        )
        if not owner_sarah.has_usable_password():
            owner_sarah.set_password('OwnerPass123!')
            owner_sarah.save()

        tenant_alice, _ = CustomUser.objects.get_or_create(
            username='tenant_alice',
            defaults={
                'email': 'alice.tenant@rentease.local',
                'role': CustomUser.Role.TENANT,
                'first_name': 'Alice',
                'last_name': 'Smith',
                'phone_number': '+1 (555) 876-5432',
                'is_verified': True,
                'occupation': 'Senior Software Engineer',
                'company_name': 'CloudScale Technologies',
                'city': 'San Francisco',
                'state': 'CA',
                'emergency_contact_name': 'Robert Smith (Father)',
                'emergency_contact_phone': '+1 (555) 999-1111',
                'bio': 'Clean and quiet professional looking for long-term residential lease.'
            }
        )
        if not tenant_alice.has_usable_password():
            tenant_alice.set_password('TenantPass123!')
            tenant_alice.save()

        tenant_david, _ = CustomUser.objects.get_or_create(
            username='tenant_david',
            defaults={
                'email': 'david.tenant@rentease.local',
                'role': CustomUser.Role.TENANT,
                'first_name': 'David',
                'last_name': 'Miller',
                'phone_number': '+1 (555) 654-3210',
                'is_verified': True,
                'occupation': 'Financial Analyst',
                'company_name': 'Horizon Asset Partners',
                'city': 'Austin',
                'state': 'TX'
            }
        )
        if not tenant_david.has_usable_password():
            tenant_david.set_password('TenantPass123!')
            tenant_david.save()

        # 3. Properties
        properties_seed = [
            {
                'owner': owner_john,
                'title': 'Skyline Luxury Penthouse with Terrace',
                'property_type': Property.PropertyType.APARTMENT,
                'status': Property.PropertyStatus.AVAILABLE,
                'address': '450 Mission Street, Unit 2802',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94105',
                'rent_amount': 3400.00,
                'security_deposit': 3400.00,
                'bedrooms': 3,
                'bathrooms': 2.5,
                'area_sqft': 1850,
                'furnished_status': Property.FurnishedStatus.FURNISHED,
                'pet_friendly': True,
                'description': 'Breathtaking 28th-floor penthouse featuring floor-to-ceiling panoramic glass windows, Italian hardwood finishes, chef kitchen with Viking appliances, private terrace, and 24/7 concierge.',
                'amenities': ['High-Speed Wi-Fi', 'Dedicated Parking Space', 'Central Air Conditioning', 'In-Unit Washer & Dryer', 'Fitness Gym', 'Private Balcony', '24/7 Security & Access Control'],
            },
            {
                'owner': owner_john,
                'title': 'Oakwood Modern Family Villa with Garden',
                'property_type': Property.PropertyType.HOUSE,
                'status': Property.PropertyStatus.RENTED,
                'address': '1284 Oakwood Glen Lane',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78704',
                'rent_amount': 2600.00,
                'security_deposit': 2600.00,
                'bedrooms': 4,
                'bathrooms': 3.0,
                'area_sqft': 2450,
                'furnished_status': Property.FurnishedStatus.SEMI_FURNISHED,
                'pet_friendly': True,
                'description': 'Spacious two-story detached home in quiet neighborhood. Open floor concept, fenced backyard with mature shade trees, solar panel roof, smart thermostat, and two-car attached garage.',
                'amenities': ['Dedicated Parking Space', 'Central Air Conditioning', 'Modern Dishwasher', 'Pet Friendly'],
            },
            {
                'owner': owner_sarah,
                'title': 'Minimalist Downtown Studio Loft',
                'property_type': Property.PropertyType.STUDIO,
                'status': Property.PropertyStatus.AVAILABLE,
                'address': '810 Arts District Boulevard, Apt 405',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78701',
                'rent_amount': 1550.00,
                'security_deposit': 1550.00,
                'bedrooms': 1,
                'bathrooms': 1.0,
                'area_sqft': 720,
                'furnished_status': Property.FurnishedStatus.FURNISHED,
                'pet_friendly': False,
                'description': 'Chic industrial loft with exposed brick walls, polished concrete flooring, 12-foot ceilings, and high-speed fiber internet. Walking distance to cafes, transit, and tech campuses.',
                'amenities': ['High-Speed Wi-Fi', 'Central Air Conditioning', 'Passenger Elevator', 'Modern Dishwasher'],
            },
            {
                'owner': owner_sarah,
                'title': 'Lakeside Waterfront Luxury Condominium',
                'property_type': Property.PropertyType.CONDO,
                'status': Property.PropertyStatus.AVAILABLE,
                'address': '220 Lakeview Marina Way, Suite 3B',
                'city': 'Seattle',
                'state': 'WA',
                'postal_code': '98109',
                'rent_amount': 2950.00,
                'security_deposit': 3000.00,
                'bedrooms': 2,
                'bathrooms': 2.0,
                'area_sqft': 1320,
                'furnished_status': Property.FurnishedStatus.FURNISHED,
                'pet_friendly': True,
                'description': 'Scenic condominium right on the marina with unobstructed sunset views. Includes access to private dock, heated indoor lap pool, sauna, and storage locker.',
                'amenities': ['Swimming Pool', 'Fitness Gym', 'Private Balcony', 'Dedicated Parking Space', 'Central Air Conditioning'],
            },
            {
                'owner': owner_john,
                'title': 'Greenfield Sunlit Suburban Townhouse',
                'property_type': Property.PropertyType.TOWNHOUSE,
                'status': Property.PropertyStatus.AVAILABLE,
                'address': '512 Meadowbrook Drive',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94122',
                'rent_amount': 2750.00,
                'security_deposit': 2750.00,
                'bedrooms': 3,
                'bathrooms': 2.0,
                'area_sqft': 1600,
                'furnished_status': Property.FurnishedStatus.UNFURNISHED,
                'pet_friendly': False,
                'description': 'Sunny end-unit townhouse with attached private patio. Renovated kitchen with quartz countertops, energy-efficient appliances, and expansive master suite.',
                'amenities': ['In-Unit Washer & Dryer', 'Dedicated Parking Space', 'Central Air Conditioning', 'Modern Dishwasher'],
            },
        ]

        created_props = []
        for p_data in properties_seed:
            amenities_list = p_data.pop('amenities')
            prop, created = Property.objects.get_or_create(
                title=p_data['title'],
                defaults=p_data
            )
            for a_name in amenities_list:
                if a_name in amenity_objs:
                    prop.amenities.add(amenity_objs[a_name])
            created_props.append(prop)

        # 4. Leases, Bookings & Applications
        # Create an active lease for tenant_alice on Property 2 (Oakwood Villa)
        oakwood_prop = created_props[1]
        app_alice, _ = RentalApplication.objects.get_or_create(
            property=oakwood_prop,
            applicant=tenant_alice,
            defaults={
                'employment_status': 'Full-Time Senior Software Engineer',
                'employer_name': 'CloudScale Technologies',
                'annual_income': 165000.00,
                'credit_score_range': 'EXCELLENT',
                'occupants_count': 2,
                'has_pets': True,
                'pets_description': '1 well-trained Golden Retriever (45 lbs)',
                'proposed_move_in': timezone.now().date() - datetime.timedelta(days=60),
                'lease_term_months': 12,
                'message_to_landlord': 'Excited to make this wonderful house our home!',
                'status': RentalApplication.ApplicationStatus.APPROVED,
                'owner_notes': 'Applicant has stellar income (10x rent) and excellent references.',
                'reviewed_at': timezone.now() - datetime.timedelta(days=59),
            }
        )

        booking_alice, _ = Booking.objects.get_or_create(
            application=app_alice,
            property=oakwood_prop,
            tenant=tenant_alice,
            defaults={
                'check_in': timezone.now().date() - datetime.timedelta(days=60),
                'deposit_amount': oakwood_prop.security_deposit,
                'status': Booking.BookingStatus.ACTIVE,
            }
        )

        lease_alice, _ = Lease.objects.get_or_create(
            booking=booking_alice,
            property=oakwood_prop,
            owner=oakwood_prop.owner,
            tenant=tenant_alice,
            defaults={
                'start_date': timezone.now().date() - datetime.timedelta(days=60),
                'end_date': timezone.now().date() + datetime.timedelta(days=305),
                'monthly_rent': oakwood_prop.rent_amount,
                'security_deposit': oakwood_prop.security_deposit,
                'rent_due_day': 1,
                'signed_by_tenant': True,
                'signed_by_owner': True,
                'signed_at': timezone.now() - datetime.timedelta(days=58),
                'status': Lease.LeaseStatus.ACTIVE,
            }
        )

        # 5. Payments for Alice's Lease
        # Past month paid rent
        Payment.objects.get_or_create(
            transaction_id='TXN-DEMO-PAID-01',
            defaults={
                'lease': lease_alice,
                'tenant': tenant_alice,
                'amount': lease_alice.monthly_rent,
                'payment_type': Payment.PaymentType.RENT,
                'payment_method': Payment.PaymentMethod.CARD,
                'description': f"Rent for {oakwood_prop.title} (Previous Month)",
                'status': Payment.PaymentStatus.PAID,
                'due_date': timezone.now().date() - datetime.timedelta(days=30),
                'paid_at': timezone.now() - datetime.timedelta(days=29),
            }
        )
        # Security Deposit paid
        Payment.objects.get_or_create(
            transaction_id='TXN-DEMO-DEPOSIT-01',
            defaults={
                'lease': lease_alice,
                'tenant': tenant_alice,
                'amount': lease_alice.security_deposit,
                'payment_type': Payment.PaymentType.SECURITY_DEPOSIT,
                'payment_method': Payment.PaymentMethod.BANK_TRANSFER,
                'description': f"Initial Security Escrow Deposit for {oakwood_prop.title}",
                'status': Payment.PaymentStatus.PAID,
                'due_date': timezone.now().date() - datetime.timedelta(days=60),
                'paid_at': timezone.now() - datetime.timedelta(days=59),
            }
        )
        # Current month pending invoice for tenant to test simulated checkout
        Payment.objects.get_or_create(
            transaction_id='TXN-DEMO-PENDING-01',
            defaults={
                'lease': lease_alice,
                'tenant': tenant_alice,
                'amount': lease_alice.monthly_rent,
                'payment_type': Payment.PaymentType.RENT,
                'payment_method': Payment.PaymentMethod.CARD,
                'description': f"Rent for {oakwood_prop.title} ({timezone.now().strftime('%B %Y')})",
                'status': Payment.PaymentStatus.PENDING,
                'due_date': timezone.now().date(),
            }
        )

        # 6. Another pending application from tenant_david on Skyline Penthouse
        skyline_prop = created_props[0]
        RentalApplication.objects.get_or_create(
            property=skyline_prop,
            applicant=tenant_david,
            defaults={
                'employment_status': 'Senior Financial Analyst',
                'employer_name': 'Horizon Asset Partners',
                'annual_income': 142000.00,
                'credit_score_range': 'GOOD',
                'occupants_count': 1,
                'has_pets': False,
                'proposed_move_in': timezone.now().date() + datetime.timedelta(days=15),
                'lease_term_months': 12,
                'message_to_landlord': 'Looking forward to moving into this unit near the financial district.',
                'status': RentalApplication.ApplicationStatus.PENDING,
            }
        )

        # 7. Maintenance tickets
        MaintenanceRequest.objects.get_or_create(
            ticket_number='TKT-DEMO-01',
            defaults={
                'property': oakwood_prop,
                'tenant': tenant_alice,
                'title': 'Kitchen garbage disposal humming but not spinning',
                'category': MaintenanceRequest.Category.APPLIANCE,
                'priority': MaintenanceRequest.Priority.MEDIUM,
                'description': 'The kitchen sink garbage disposal unit hums when turned on but does not rotate. Disconnected the unit safely for now.',
                'status': MaintenanceRequest.Status.IN_PROGRESS,
                'landlord_response': 'Technician scheduled to visit Tuesday between 10am-12pm. Dispatched Apex Appliance Care ticket #9921.',
            }
        )
        MaintenanceRequest.objects.get_or_create(
            ticket_number='TKT-DEMO-02',
            defaults={
                'property': oakwood_prop,
                'tenant': tenant_alice,
                'title': 'HVAC filter replacement required',
                'category': MaintenanceRequest.Category.HVAC,
                'priority': MaintenanceRequest.Priority.LOW,
                'description': 'Routine 6-month air filter change. Could replacement filters be dispatched?',
                'status': MaintenanceRequest.Status.SUBMITTED,
            }
        )

        self.stdout.write(self.style.SUCCESS("Demo database successfully populated with realistic properties, leases, payments, tickets, and accounts!"))


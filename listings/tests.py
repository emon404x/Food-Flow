from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from locations.models import Location
from accounts.models import Donor
from listings.models import FoodListing
from listings.services import ExpiryService
from listings.forms import FoodListingForm

User = get_user_model()


class ListingsModelAndServiceTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(address="55 Lake Rd", area="Gulshan", city="Dhaka")
        self.donor_user = User.objects.create_user(
            username="donor_cafe",
            full_name="Green Cafe",
            email="cafe@test.com",
            password="pwd",
            role="donor"
        )
        self.donor = Donor.objects.create(
            user=self.donor_user,
            donor_type="restaurant",
            organization_name="Green Cafe",
            location=self.location,
            is_verified=True
        )

    def test_food_listing_creation_defaults(self):
        """Test creating an available food listing."""
        listing = FoodListing.objects.create(
            donor=self.donor,
            location=self.location,
            food_name="Fresh Bread Loaves",
            description="Warm bakery bread",
            quantity=Decimal("15.00"),
            unit="loaves",
            expires_at=timezone.now() + timedelta(hours=8),
            status=FoodListing.STATUS_AVAILABLE
        )
        self.assertEqual(listing.status, FoodListing.STATUS_AVAILABLE)
        self.assertFalse(listing.is_expired)
        self.assertEqual(listing.quantity_available, Decimal("15.00"))

    def test_visible_to_recipients_filters_expired_listings(self):
        """Test that visible_to_recipients excludes expired items."""
        # Active listing
        active = FoodListing.objects.create(
            donor=self.donor,
            location=self.location,
            food_name="Vegetable Rice",
            description="Freshly cooked",
            quantity=Decimal("10.00"),
            unit="boxes",
            expires_at=timezone.now() + timedelta(hours=4),
            status=FoodListing.STATUS_AVAILABLE
        )

        # Expired listing
        expired = FoodListing.objects.create(
            donor=self.donor,
            location=self.location,
            food_name="Cooked Pasta",
            description="Expired pasta",
            quantity=Decimal("5.00"),
            unit="boxes",
            expires_at=timezone.now() - timedelta(minutes=15),
            status=FoodListing.STATUS_AVAILABLE
        )

        visible = FoodListing.visible_to_recipients()
        self.assertTrue(visible.filter(pk=active.pk).exists())
        self.assertFalse(visible.filter(pk=expired.pk).exists())

    def test_expiry_service_marks_expired_listings(self):
        """Test that ExpiryService transitions past listings to STATUS_EXPIRED."""
        past_listing = FoodListing.objects.create(
            donor=self.donor,
            location=self.location,
            food_name="Overnight Salad",
            description="Prepared yesterday",
            quantity=Decimal("8.00"),
            unit="bowls",
            expires_at=timezone.now() - timedelta(minutes=5),
            status=FoodListing.STATUS_AVAILABLE
        )

        updated = ExpiryService.check_and_update_listing_expiration(past_listing)
        self.assertTrue(updated)
        past_listing.refresh_from_db()
        self.assertEqual(past_listing.status, FoodListing.STATUS_EXPIRED)

    def test_listing_form_rejects_past_or_too_soon_expiry(self):
        """Test that form rejects past expiry dates or expiry within 30 minutes."""
        now = timezone.now()
        form_data = {
            'food_name': 'Test Item',
            'quantity': '10',
            'unit': 'kg',
            'expires_at': (now + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M'),  # < 30 minutes
            'address': 'Test Rd',
            'area': 'Gulshan',
            'city': 'Dhaka',
        }
        form = FoodListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('expires_at', form.errors)

    def test_listing_form_accepts_valid_data(self):
        """Test valid food listing form submission."""
        now = timezone.now()
        form_data = {
            'food_name': 'Fresh Apples',
            'quantity': '25.5',
            'unit': 'kg',
            'expires_at': (now + timedelta(hours=10)).strftime('%Y-%m-%dT%H:%M'),
            'address': 'Road 11',
            'area': 'Banani',
            'city': 'Dhaka',
        }
        form = FoodListingForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

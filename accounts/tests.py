from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from locations.models import Location
from accounts.models import Donor, Recipient

User = get_user_model()


class AccountsModelAndAuthTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            address="123 Green Rd",
            area="Dhanmondi",
            city="Dhaka"
        )

    def test_custom_user_creation_and_roles(self):
        donor_user = User.objects.create_user(
            username="donor1",
            full_name="Donor One",
            email="donor1@test.com",
            password="Password123",
            role=User.ROLE_DONOR,
            phone="+8801700000001"
        )
        self.assertTrue(donor_user.is_donor)
        self.assertFalse(donor_user.is_recipient)
        self.assertEqual(donor_user.full_name, "Donor One")
        # Verify password is encrypted/hashed
        self.assertTrue(donor_user.password.startswith('pbkdf2_') or donor_user.password.startswith('argon2'))
        self.assertTrue(donor_user.check_password("Password123"))

        donor_profile = Donor.objects.create(
            user=donor_user,
            donor_type="restaurant",
            organization_name="Tasty Bites",
            location=self.location,
            is_verified=False
        )
        self.assertEqual(donor_user.donor_profile.organization_name, "Tasty Bites")
        self.assertFalse(donor_profile.is_verified)

    def test_registration_donor_flow(self):
        """Test complete registration flow for donor with full_name and password hashing."""
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Fresh Eats Donor',
            'username': 'newdonor',
            'email': 'newdonor@test.com',
            'phone': '+8801999999999',
            'role': 'donor',
            'donor_type': 'restaurant',
            'organization_name': 'Fresh Eats',
            'address': '45 Lake View',
            'area': 'Gulshan',
            'city': 'Dhaka',
            'password': 'Password123',
            'password_confirm': 'Password123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='newdonor')
        self.assertTrue(user.is_donor)
        self.assertEqual(user.full_name, 'Fresh Eats Donor')
        self.assertTrue(check_password('Password123', user.password))
        self.assertFalse(user.donor_profile.is_verified)
        self.assertEqual(user.donor_profile.organization_name, 'Fresh Eats')
        self.assertEqual(user.donor_profile.location.city, 'Dhaka')
        # Check automatic login into donor dashboard
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_registration_recipient_flow(self):
        """Test complete registration flow for recipient with profile created unverified."""
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Hope Shelter',
            'username': 'newrecipient',
            'email': 'recipient@test.com',
            'phone': '+8801888888888',
            'role': 'recipient',
            'recipient_type': 'shelter',
            'address': '12 Hope St',
            'area': 'Mirpur',
            'city': 'Dhaka',
            'password': 'Password123',
            'password_confirm': 'Password123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='newrecipient')
        self.assertTrue(user.is_recipient)
        self.assertEqual(user.full_name, 'Hope Shelter')
        self.assertFalse(user.recipient_profile.is_verified)
        self.assertEqual(user.recipient_profile.recipient_type, 'shelter')
        self.assertEqual(user.recipient_profile.location.area, 'Mirpur')

    def test_registration_password_mismatch_rejection(self):
        """Test that mismatched passwords fail registration."""
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Mismatch Test',
            'username': 'mismatchuser',
            'email': 'mismatch@test.com',
            'role': 'recipient',
            'recipient_type': 'individual',
            'address': 'Street 1',
            'area': 'Area 1',
            'city': 'Dhaka',
            'password': 'Password123',
            'password_confirm': 'DifferentPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())
        self.assertFormError(response.context['form'], 'password_confirm', "Passwords do not match.")

    def test_registration_duplicate_username_rejection(self):
        """Test that registering an existing username is rejected."""
        User.objects.create_user(username='existinguser', email='first@test.com', password='Password123')
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Duplicate User',
            'username': 'existinguser',
            'email': 'second@test.com',
            'role': 'donor',
            'donor_type': 'household',
            'address': 'Street 2',
            'area': 'Area 2',
            'city': 'Dhaka',
            'password': 'Password123',
            'password_confirm': 'Password123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', "A user with that username already exists.")

    def test_registration_duplicate_email_rejection(self):
        """Test that registering an existing email is rejected."""
        User.objects.create_user(username='userone', email='common@test.com', password='Password123')
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Second User',
            'username': 'usertwo',
            'email': 'common@test.com',
            'role': 'donor',
            'donor_type': 'household',
            'address': 'Street 3',
            'area': 'Area 3',
            'city': 'Dhaka',
            'password': 'Password123',
            'password_confirm': 'Password123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', "An account with this email already exists.")

    def test_login_with_username_success(self):
        """Test successful authentication using username."""
        donor_u = User.objects.create_user(username='testdonor', email='donor@test.com', password='Password123', role='donor')
        Donor.objects.create(user=donor_u, donor_type='restaurant', location=self.location, is_verified=True)
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testdonor',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:donor_dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_with_email_success(self):
        """Test successful authentication using email address instead of username."""
        rec_u = User.objects.create_user(username='testrecipient', email='recipient_unique@test.com', password='Password123', role='recipient')
        Recipient.objects.create(user=rec_u, recipient_type='individual', location=self.location, is_verified=True)
        response = self.client.post(reverse('accounts:login'), {
            'username': 'recipient_unique@test.com',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:recipient_dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_wrong_password_failure(self):
        """Test authentication rejection with wrong password."""
        User.objects.create_user(username='userx', email='userx@test.com', password='CorrectPassword123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'userx',
            'password': 'WrongPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_unknown_user_failure(self):
        """Test rejection of non-existent username."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'nonexistent_user',
            'password': 'AnyPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_flow(self):
        """Test logging out properly clears the session."""
        user = User.objects.create_user(username='logoutuser', email='logout@test.com', password='Password123')
        self.client.force_login(user)
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_authenticated_user_visiting_login_redirects(self):
        """Test that logged-in users visiting login or register are redirected to their dashboard."""
        donor_user = User.objects.create_user(username='activedonor', email='ad@test.com', password='Password123', role='donor')
        Donor.objects.create(user=donor_user, donor_type='restaurant', location=self.location, is_verified=True)
        self.client.force_login(donor_user)

        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:donor_dashboard'))

        response_reg = self.client.get(reverse('accounts:register'))
        self.assertEqual(response_reg.status_code, 302)
        self.assertRedirects(response_reg, reverse('accounts:donor_dashboard'))

    def test_admin_user_redirection_to_admin_index(self):
        """Test that staff/superuser is redirected to admin panel upon login."""
        admin_user = User.objects.create_superuser(username='superadmin', email='sa@test.com', password='AdminPassword123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'superadmin',
            'password': 'AdminPassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin:index'))

    def test_admin_verification_workflow(self):
        """Test administrator verification of recipient and donor accounts."""
        rec_user = User.objects.create_user(username='rec_verify', email='rv@test.com', password='Password123', role='recipient')
        rec = Recipient.objects.create(user=rec_user, recipient_type='ngo', location=self.location, is_verified=False)
        self.assertFalse(rec.is_verified)

        # Admin approves recipient
        rec.is_verified = True
        rec.save(update_fields=['is_verified'])

        # Verify from persistent database
        reloaded_rec = Recipient.objects.get(pk=rec.pk)
        self.assertTrue(reloaded_rec.is_verified)

    def test_profile_update_duplicate_email_rejected(self):
        """Test that updating user profile cannot use an already registered email."""
        user1 = User.objects.create_user(username='u1', email='first@test.com', password='Password123')
        user2 = User.objects.create_user(username='u2', email='second@test.com', password='Password123')
        self.client.force_login(user2)

        response = self.client.post(reverse('accounts:profile'), {
            'full_name': 'Updated Name',
            'email': 'first@test.com',  # Already taken by user1
            'phone': '123456',
            'address': 'Test Rd',
            'area': 'Test Area',
            'city': 'Dhaka',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', "An account with this email already exists.")
        user2.refresh_from_db()
        self.assertEqual(user2.email, 'second@test.com')


class DatabaseConfigTests(TestCase):
    def test_local_sqlite_settings(self):
        """Verify that local development uses SQLite."""
        from django.conf import settings
        self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')

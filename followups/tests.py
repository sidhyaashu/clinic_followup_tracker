from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import Clinic, UserProfile, FollowUp, PublicViewLog

# Create your tests here.
class ClinicModelTest(TestCase):
    def test_clinic_code_is_generated_and_unique(self):
        clinic1 = Clinic.objects.create(name="Clinic A")
        clinic2 = Clinic.objects.create(name="Clinic B")

        self.assertIsNotNone(clinic1.clinic_code)
        self.assertIsNotNone(clinic2.clinic_code)
        
        self.assertNotEqual(clinic1.clinic_code, clinic2.clinic_code)
        
class FollowUpTokenTest(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(name="Test Clinic")
        self.user = User.objects.create_user(
            username="user1", password="pass123"
        )
        UserProfile.objects.create(user=self.user, clinic=self.clinic)

    def test_public_token_is_generated_and_unique(self):
        f1 = FollowUp.objects.create(
            clinic=self.clinic,
            created_by=self.user,
            patient_name="Patient 1",
            phone="9999999999",
            language="en",
            due_date=date.today()
        )

        f2 = FollowUp.objects.create(
            clinic=self.clinic,
            created_by=self.user,
            patient_name="Patient 2",
            phone="8888888888",
            language="en",
            due_date=date.today()
        )

        self.assertNotEqual(f1.public_token, f2.public_token)


class DashboardAuthTest(TestCase):
    def test_dashboard_requires_login(self):
        client = Client()
        response = client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class CrossClinicAccessTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.clinic1 = Clinic.objects.create(name="Clinic 1")
        self.clinic2 = Clinic.objects.create(name="Clinic 2")

        self.user1 = User.objects.create_user(
            username="user1", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123"
        )

        UserProfile.objects.create(user=self.user1, clinic=self.clinic1)
        UserProfile.objects.create(user=self.user2, clinic=self.clinic2)

        self.followup = FollowUp.objects.create(
            clinic=self.clinic1,
            created_by=self.user1,
            patient_name="Patient X",
            phone="9999999999",
            language="en",
            due_date=date.today()
        )

    def test_user_cannot_access_other_clinic_followup(self):
        self.client.login(username="user2", password="pass123")

        response = self.client.get(
            reverse("followup_edit", args=[self.followup.id])
        )

        self.assertEqual(response.status_code, 404)


class PublicViewLogTest(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(name="Clinic")
        self.user = User.objects.create_user(
            username="user", password="pass123"
        )
        UserProfile.objects.create(user=self.user, clinic=self.clinic)

        self.followup = FollowUp.objects.create(
            clinic=self.clinic,
            created_by=self.user,
            patient_name="Patient",
            phone="9999999999",
            language="en",
            due_date=date.today()
        )

    def test_public_page_creates_view_log(self):
        client = Client()
        url = reverse("public_followup", args=[self.followup.public_token])

        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            PublicViewLog.objects.filter(followup=self.followup).count(),
            1
        )


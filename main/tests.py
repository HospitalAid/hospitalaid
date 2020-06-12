from django.core import mail
from django.urls import reverse
from django_webtest import WebTest

from main import models


class TestPage(WebTest):
    def test_home_page_works(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class TestSignup(WebTest):
    def test_user_signup_page_submission_works(self):
        signup_form = self.app.get(reverse("signup")).form
        signup_form["email"] = "user@domain.com"
        response = signup_form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.User.objects.filter(email="user@domain.com").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hospital Aid Login Link")

    def test_step2_create_hospital_if_not_exists(self):
        user1 = models.User.objects.create_user("user1@domain.com", "pw432joij")
        step2_form = self.app.get(reverse("signup_step2"), user=user1).form
        step2_form["name"] = "John smith"
        step2_form["phone"] = "123"
        step2_form["hospital_name"] = "Red cross"
        step2_form["hospital_address"] = "1 road street"
        step2_form["hospital_city"] = "London"
        step2_form["hospital_postcode"] = "XXX"
        step2_form["hospital_country"] = "UK"
        step2_form["hospital_latitude"] = 12.1
        step2_form["hospital_longitude"] = 22.1
        step2_form.submit()

        hospital = models.main.Hospital.objects.get(user=user1)
        self.assertEqual(hospital.name, "Red cross")

    def test_step2_change_hospital_if_exists(self):
        user1 = models.User.objects.create_user("user1@domain.com", "pw432joij")
        models.main.Hospital.objects.create(
            user=user1,
            name="White cross",
            address="2 black st",
            city="London",
            postal_code="?",
            country="KKK",
            latitude=1.1,
            longitude=2.2,
        )

        step2_form = self.app.get(reverse("signup_step2"), user=user1).form
        step2_form["name"] = "John smith"
        step2_form["phone"] = "123"
        step2_form["hospital_name"] = "White cross"
        step2_form["hospital_address"] = "1 road street"
        step2_form["hospital_city"] = "London"
        step2_form["hospital_postcode"] = "XXX"
        step2_form["hospital_country"] = "UK"
        step2_form["hospital_latitude"] = 12.1
        step2_form["hospital_longitude"] = 22.1
        step2_form.submit()

        hospital = models.main.Hospital.objects.get(user=user1)
        self.assertEqual(hospital.name, "White cross")


class TestHospitalViews(WebTest):
    def setUp(self):
        user1 = models.User.objects.create_user("user1@domain.com", "pw432joij")
        user1.first_name = "John Smith"
        user1.phone = "012345"
        user1.save()
        hospital = models.Hospital.objects.create(
            user=user1,
            name="Red cross",
            address="1 road street",
            city="London",
            postal_code="XXX",
            country="United kingodm",
            latitude=12.1,
            longitude=22.3,
        )
        self.app.set_user(user1)
        self.hospital = hospital

    def test_add_aidrequest(self):
        response = self.app.get("/").follow()
        add_form = response.click("Add a new request").form
        add_form["type"] = "supply"
        add_form["title"] = "masks"
        add_form["quantity"] = 12
        add_form["comments"] = "bla bla bla"
        add_form.submit()

        aid = models.main.AidRequest.objects.get(hospital=self.hospital)
        self.assertEqual(aid.title, "masks")

    def test_change_status_to_aidrequest(self):
        aid = {}
        aid["type"] = "supply"
        aid["title"] = "masks"
        aid["quantity"] = 12
        aid["comments"] = "bla bla bla"
        aid["hospital"] = self.hospital
        aid = models.main.AidRequest.objects.create(**aid)

        self.app.get(
            reverse("aidrequest_status", kwargs={"pk": aid.id, "value": "closed"})
        ).follow()

        aid = models.main.AidRequest.objects.get(id=aid.id)
        self.assertEqual(aid.status, "closed")

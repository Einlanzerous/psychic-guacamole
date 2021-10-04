import json
import pytest
from unittest import TestCase

from django.test import Client
from django.urls import reverse

from api.coronavstech.companies.models import Company


@pytest.mark.django_db
class BaseCompanyAPITestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.companies_url = reverse("companies-list")

    def tearDown(self) -> None:
        pass


class TestGetCompanies(BaseCompanyAPITestCase):
    def test_zero_companies_should_return_empty_list(self) -> None:
        response = self.client.get(self.companies_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_one_company_exists_should_succeed(self) -> None:
        test_company = Company.objects.create(name="Amazon")

        response = self.client.get(self.companies_url)
        response_content = json.loads(response.content)[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get("name"), test_company.name)
        self.assertEqual(response_content.get("status"), test_company.status)
        self.assertEqual(
            response_content.get("application_link"), test_company.application_link
        )
        self.assertEqual(response_content.get("notes"), test_company.notes)


class TestPostCompanies(BaseCompanyAPITestCase):
    def test_create_company_without_arguments_should_fail(self) -> None:
        response = self.client.post(path=self.companies_url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content), {"name": ["This field is required."]}
        )

    def test_create_existing_company_should_fail(self) -> None:
        Company.objects.create(name="Microsoft")

        response = self.client.post(path=self.companies_url, data={"name": "Microsoft"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"name": ["company with this name already exists."]},
        )

    def test_create_company_with_name_only_all_fields_should_default(self) -> None:
        response = self.client.post(
            path=self.companies_url, data={"name": "Test Company Name"}
        )

        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("name"), "Test Company Name")
        self.assertEqual(response_content.get("application_link"), "")
        self.assertEqual(response_content.get("notes"), "")

    def test_create_company_with_layoffs_status_should_succeed(self) -> None:
        response = self.client.post(
            path=self.companies_url,
            data={"name": "A Layoffs Company", "status": "Layoffs"},
        )

        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("status"), "Layoffs")

    def test_create_company_with_invalid_status_should_fail(self) -> None:
        response = self.client.post(
            path=self.companies_url,
            data={"name": "Invalid Status Company", "status": "invalid"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid", str(response.content))
        self.assertIn("is not a valid choice", str(response.content))

    @pytest.mark.xfail
    def test_should_be_ok_if_fails(self) -> None:
        self.assertEqual(1, 2)


import logging

logger = logging.getLogger("CORONA_LOGS")


def function_that_logs_something() -> None:
    logger.warning(f"I am logging")


def test_logged_warning_level(caplog) -> None:
    function_that_logs_something()
    assert "I am logging" in caplog.text

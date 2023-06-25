from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client

from ..models import Schema, Separator, DataType, Column


class TestView(TestCase):
    """
    Base Class for testing
    """
    url_name = ''
    url_kwargs = {}

    dummy_username = 'dummy_test_user'
    dummy_password = '32145'
    dummy_email = 'dummy@gmail.com'

    schema_name = 'test_schema'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.url = reverse(viewname=cls.url_name, kwargs=cls.url_kwargs)

        cls.user = User.objects.create_user(
            username=cls.dummy_username,
            password=cls.dummy_password,
            email=cls.dummy_email,
        )

        cls.delimiter = Separator.objects.create(name='dot', char='.')
        cls.quotechar = Separator.objects.create(name='double-quote', char='"')

        cls.data_type_1 = DataType.objects.create(
            name='Word',
            have_limits=True,
        )
        cls.data_type_2 = DataType.objects.create(
            name='Sentence',
            have_limits=True,
        )

        cls.schema = Schema.objects.create(
            name=cls.schema_name,
            owner=cls.user,
            delimiter=cls.delimiter,
            quotechar=cls.quotechar,
        )

        cls.column_1 = Column.objects.create(
            name='first',
            minimal=1,
            maximal=10,
            data_type=cls.data_type_1,
            schema=cls.schema,
        )
        cls.column_2 = Column.objects.create(
            name='second',
            minimal=2,
            maximal=8,
            data_type=cls.data_type_2,
            schema=cls.schema,
            order=2,
        )


class NotAuthorisedMixin:
    def test_GET_not_authorised(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('login') + '?next=' + self.url)


class AuthorisedMixin:
    template_name = ''

    def test_GET_authorised(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class AuthorisedNotOwnerMixin:
    dummy_2_username = 'second_user'
    dummy_2_password = '54321'
    dummy_2_email = 'seconduser@gmail.com'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_user = User.objects.create_user(
            username=cls.dummy_2_username,
            password=cls.dummy_2_password,
            email=cls.dummy_2_email,
        )

    def test_GET_authorised_not_owner(self):
        self.client.login(username=self.dummy_2_username, password=self.dummy_2_password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)


class JsonPostErrorResponsesMixin:
    dummy_2_username = 'second_user'
    dummy_2_password = '54321'
    dummy_2_email = 'seconduser@gmail.com'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_user = User.objects.create_user(
            username=cls.dummy_2_username,
            password=cls.dummy_2_password,
            email=cls.dummy_2_email,
        )

    def test_GET_method_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_POST_not_authenticated(self):
        response = self.client.post(self.url, {'schema': self.schema.slug})

        self.assertEqual(response.status_code, 404)

    def test_POST_not_existing_schema(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url, {'schema': self.schema.slug + 'not_existing'})

        self.assertEqual(response.status_code, 404)

    def test_POST_authenticated_not_owner(self):
        self.client.login(username=self.dummy_2_username, password=self.dummy_2_password)
        response = self.client.post(self.url, {'schema': self.schema.slug})

        self.assertEqual(response.status_code, 404)

from django.contrib.auth.models import User
from django.test import TestCase

from ..forms import SeparatorForm, SchemaForm, ColumnFormSet, RegisterUserForm
from ..models import Separator, Column


class TestRegisterUserForm(TestCase):
    new_user_username = 'new_test_user'
    new_user_password = 'i3oi34mi34iomo34im'
    new_user_email = 'sdkfd@gmail.com'

    def tearDown(self):
        user = User.objects.filter(username=self.new_user_username)
        if user:
            user.delete()

    def test_valid_data(self):
        data = {
            'username': self.new_user_username,
            'password1': self.new_user_password,
            'password2': self.new_user_password,
            'email': self.new_user_email,
        }
        form = RegisterUserForm(data=data)

        self.assertTrue(form.is_valid())

    def test_no_data(self):
        form = RegisterUserForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)

    def test_not_same_passwords(self):
        data = {
            'username': self.new_user_username,
            'password1': self.new_user_password,
            'password2': 'efergkergriopgdfopjk',
            'email': self.new_user_email,
        }
        form = RegisterUserForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

    def test_user_already_exists(self):
        User.objects.create_user(username=self.new_user_username, email='jeirj3p@gmail.com', password='i3oi34mi34g34im')

        data = {
            'username': self.new_user_username,
            'password1': self.new_user_password,
            'password2': self.new_user_password,
            'email': self.new_user_email,
        }
        form = RegisterUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)


class TestSeparatorForm(TestCase):
    def test_valid_data(self):
        data = {
            'name': 'Some Name',
            'char': 'k',
        }
        form = SeparatorForm(data=data)

        self.assertTrue(form.is_valid())

    def test_no_data(self):
        form = SeparatorForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)


class TestSchemaForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.delimiter = Separator.objects.create(name='test1', char='1')
        cls.quotechar = Separator.objects.create(name='test2', char='2')

    def test_valid_data(self):
        data = {
            'name': 'Some Name',
            'delimiter': self.delimiter.pk,
            'quotechar': self.quotechar.pk,
        }
        form = SchemaForm(data=data)

        self.assertTrue(form.is_valid())

    def test_no_data(self):
        form = SchemaForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)


class TestColumnFormSet(TestCase):
    def test_valid_data(self):
        data = {
            'columns-TOTAL_FORMS': 2,
            'columns-INITIAL_FORMS': 0,
            'columns-MIN_NUM': 0,
            'columns-MAX_NUM_FORMS': 1000,
            'columns-0-name': 'Column1',
            'columns-0-data_type': Column.DataType.FULL_NAME,
            'columns-0-ORDER': 1,
            'columns-1-name': 'Column2',
            'columns-1-minimal': 0,
            'columns-1-maximal': 10,
            'columns-1-data_type': Column.DataType.TEXT,
            'columns-1-ORDER': 2,
        }
        formset = ColumnFormSet(data=data)

        self.assertTrue(formset.is_valid())

    def test_no_data(self):
        formset = ColumnFormSet(data={})

        self.assertFalse(formset.is_valid())

    def test_no_limits_where_needs(self):
        data = {
            'columns-TOTAL_FORMS': 2,
            'columns-INITIAL_FORMS': 0,
            'columns-MIN_NUM': 0,
            'columns-MAX_NUM_FORMS': 1000,
            'columns-0-name': 'Column1',
            'columns-0-data_type': Column.DataType.FULL_NAME,
            'columns-0-ORDER': 1,
            'columns-1-name': 'Column2',
            # 'columns-1-minimal': 0,
            # 'columns-1-maximal': 10,
            'columns-1-data_type': Column.DataType.INTEGER,
            'columns-1-ORDER': 2,
        }
        formset = ColumnFormSet(data=data)

        self.assertFalse(formset.is_valid())

    def test_no_data_type_where_needs(self):
        data = {
            'columns-TOTAL_FORMS': 2,
            'columns-INITIAL_FORMS': 0,
            'columns-MIN_NUM': 0,
            'columns-MAX_NUM_FORMS': 1000,
            'columns-0-name': 'Column1',
            'columns-0-ORDER': 1,
            'columns-1-name': 'Column2',
            'columns-1-ORDER': 2,
        }
        formset = ColumnFormSet(data=data)

        self.assertFalse(formset.is_valid())

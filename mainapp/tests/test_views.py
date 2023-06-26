import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .test_view_base_and_mixins import TestView, AuthorisedNotOwnerMixin, AuthorisedMixin, NotAuthorisedMixin, \
    JsonPostErrorResponsesMixin
from ..forms import SchemaForm, ColumnFormSet
from ..models import Schema, Column, DataSet


class TestUserLoginView(TestView):
    url_name = 'login'

    def test_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/login.html')

    def test_POST_authorises(self):
        response = self.client.post(self.url, {'username': self.dummy_username, 'password': self.dummy_password})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.assertRedirects(response, reverse('schema-list'))

    def test_POST_redirects_to_next(self):
        next_page_url = reverse('schema-data-sets', kwargs={'schema_slug': self.schema.slug})
        response = self.client.post(
            self.url + '?next=' + next_page_url,
            {'username': self.dummy_username, 'password': self.dummy_password}
        )

        self.assertRedirects(response, next_page_url)


class TestLogout(TestView):
    url_name = 'logout'

    def test_logout_user_and_redirects(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.get(self.url)

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.assertRedirects(response, reverse('login'))


class TestSchemasView(NotAuthorisedMixin, AuthorisedMixin, TestView):
    url_name = 'schema-list'
    template_name = 'mainapp/schemas.html'

    def test_GET_queryset(self):
        wrong_user = User.objects.create_user(
            username='wrong',
            password='9887654',
            email='wrong@gmail.com',
        )
        Schema.objects.create(name='wrong_schema_1', owner=wrong_user,
                              delimiter=self.delimiter, quotechar=self.quotechar)
        Schema.objects.create(name='wrong_schema_2', owner=wrong_user,
                              delimiter=self.delimiter, quotechar=self.quotechar)
        Schema.objects.create(name='test_schema_2', owner=self.user,
                              delimiter=self.delimiter, quotechar=self.quotechar)

        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.get(self.url)

        self.assertQuerysetEqual(response.context.get('schemas'), self.user.schemas.all(), ordered=False)


class TestCreateSchemaView(NotAuthorisedMixin, AuthorisedMixin, TestView):
    url_name = 'create-schema'
    template_name = 'mainapp/schema_form.html'

    def test_GET_context(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.get(self.url)

        self.assertTrue(isinstance(response.context.get('form'), SchemaForm))
        self.assertTrue(isinstance(response.context.get('formset'), ColumnFormSet))
        self.assertEqual(response.context.get('data_types_need_limits'), [1, 2])

    def test_POST_creates_new_schema(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        schema_name = 'new_schema'
        column_1_name = 'Column_1'
        column_2_name = 'Column_2'

        data = {
            'name': schema_name,
            'delimiter': self.delimiter.pk,
            'quotechar': self.quotechar.pk,
            'columns-TOTAL_FORMS': 2,
            'columns-INITIAL_FORMS': 0,
            'columns-MIN_NUM': 0,
            'columns-MAX_NUM_FORMS': 1000,
            'columns-0-name': column_1_name,
            'columns-0-data_type': self.data_type_1.pk,
            'columns-0-minimal': 2,
            'columns-0-maximal': 8,
            'columns-0-ORDER': 1,
            'columns-1-name': column_2_name,
            'columns-1-minimal': 0,
            'columns-1-maximal': 10,
            'columns-1-data_type': self.data_type_2.pk,
            'columns-1-ORDER': 2,
        }
        response = self.client.post(self.url, data)

        self.assertEqual(self.user.schemas.last().name, schema_name)
        self.assertEqual(self.user.schemas.last().columns.first().name, column_1_name)
        self.assertEqual(self.user.schemas.last().columns.last().name, column_2_name)
        self.assertEqual(self.user.schemas.last().columns.count(), 2)
        self.assertRedirects(response, reverse('schema-data-sets', kwargs={'schema_slug': schema_name}))

    def test_POST_no_data(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.schemas.count(), 1)


class TestEditSchemaView(NotAuthorisedMixin, AuthorisedMixin, AuthorisedNotOwnerMixin, TestView):
    url_name = 'edit-schema'
    template_name = 'mainapp/schema_form.html'
    url_kwargs = {'schema_slug': TestView.schema_name}

    def test_GET_context(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.get(self.url)

        self.assertTrue(isinstance(response.context.get('form'), SchemaForm))
        self.assertTrue(isinstance(response.context.get('formset'), ColumnFormSet))
        self.assertEqual(response.context.get('data_types_need_limits'), [1, 2])

    def test_POST_edits_schema_and_columns(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        column_1 = self.schema.columns.first()
        column_2 = self.schema.columns.last()

        data = {
            'name': self.schema.name + '_edited',
            'delimiter': self.delimiter.pk,
            'quotechar': self.quotechar.pk,
            'columns-TOTAL_FORMS': 3,
            'columns-INITIAL_FORMS': 2,
            'columns-MIN_NUM': 0,
            'columns-MAX_NUM_FORMS': 1000,
            'columns-0-id': column_1.pk,
            'columns-0-name': column_1.name + '_edited',
            'columns-0-data_type': column_1.data_type.pk,
            'columns-0-minimal': 2,
            'columns-0-maximal': 8,
            'columns-0-ORDER': 1,
            'columns-1-id': column_2.pk,
            'columns-1-name': column_2.name,
            'columns-1-minimal': 100,
            'columns-1-maximal': 101,
            'columns-1-data_type': column_2.data_type.pk,
            'columns-1-ORDER': 3,
            'columns-1-DELETE': True,
            'columns-2-name': 'column_3',
            'columns-2-data_type': column_1.data_type.pk,
            'columns-2-minimal': 0,
            'columns-2-maximal': 3,
            'columns-2-ORDER': 2,
        }
        response = self.client.post(self.url, data)

        self.schema.refresh_from_db()
        self.column_1.refresh_from_db()

        self.assertEqual(self.schema.name, self.schema_name + '_edited')
        self.assertEqual(self.column_1.name, 'first_column_test_view_edited')
        self.assertRaises(ObjectDoesNotExist, self.column_2.refresh_from_db)
        self.assertEqual(self.schema.columns.count(), 2)
        self.assertRedirects(response, reverse('schema-data-sets', kwargs={'schema_slug': self.schema.slug}))

    def test_POST_no_data(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)


class TestSchemaDataSets(NotAuthorisedMixin, AuthorisedMixin, AuthorisedNotOwnerMixin, TestView):
    url_name = 'schema-data-sets'
    template_name = 'mainapp/schema_data_sets.html'
    url_kwargs = {'schema_slug': TestView.schema_name}

    def test_GET_queryset(self):
        wrong_schema = Schema.objects.create(name='wrong_schema', owner=self.second_user,
                                             delimiter=self.delimiter, quotechar=self.quotechar)
        Column.objects.create(name='wrong_column_1', schema=wrong_schema, data_type=self.data_type_1,
                              minimal=1, maximal=10)
        Column.objects.create(name='wrong_column_2', schema=wrong_schema, data_type=self.data_type_1,
                              minimal=2, maximal=5)

        DataSet.objects.create(schema=wrong_schema)
        DataSet.objects.create(schema=wrong_schema)

        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.get(self.url)

        self.assertQuerysetEqual(response.context.get('object_list'), self.schema.data_sets.all(), ordered=False)

    def test_GET_context(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)

        response = self.client.get(self.url)

        self.assertEqual(response.context.get('schema'), self.schema)


class TestDownload(AuthorisedNotOwnerMixin, TestView):
    url_name = 'download'

    def test_POST_method_not_allowed(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)

    def test_GET_not_generated_file(self):
        data_set = DataSet.objects.create(schema=self.schema)

        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.get(self.url, data={'data_set': data_set.pk})

        self.assertEqual(response.status_code, 404)

    def test_GET_file_downloads(self):
        test_scv_file = SimpleUploadedFile('test.csv', b'123gjgh')
        data_set = DataSet.objects.create(schema=self.schema, file=test_scv_file)

        try:
            self.client.login(username=self.dummy_username, password=self.dummy_password)
            response = self.client.get(self.url, data={'data_set': data_set.pk})

            self.assertEqual(response.get('Content-Disposition'), f"attachment; filename=\"test.csv\"")

        finally:
            data_set.file.delete()


class TestDeleteSchema(JsonPostErrorResponsesMixin, TestView):
    url_name = 'delete-schema'

    def test_POST_schema_deletes(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url, {'schema': self.schema.slug})

        self.assertEqual(response.status_code, 200)
        self.assertRaises(ObjectDoesNotExist, self.schema.refresh_from_db)


class TestStartGenerating(JsonPostErrorResponsesMixin, TestView):
    url_name = 'data-set-start-generating'

    def tearDown(self):
        if self.schema.data_sets and self.schema.data_sets.first().file:
            self.schema.data_sets.first().file.delete()

    def test_POST_rows_not_set(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url, {'schema': self.schema.slug})

        self.assertEqual(response.status_code, 400)

    def test_POST_rows_less_than_1(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url, {'schema': self.schema.slug, 'rows': 0})

        self.assertEqual(response.status_code, 400)

    def test_POST_file_generated_successfully(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.post(self.url, {'schema': self.schema.slug, 'rows': 5})

        self.assertEqual(response.status_code, 200)

        try:
            data_set = DataSet.objects.get(pk=json.loads(response.content).get('data_set_id'))
        except:
            self.fail("DataSet object was not created")

        self.assertTrue(data_set.file)

        try:
            file_generated_message = json.loads(response.content).get('file_generated')
        except:
            self.fail("Something wrong with response")

        self.assertTrue(file_generated_message)


class TestGetGeneratingStatuses(TestView):
    url_name = 'get-generating-data-sets'

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

    def test_POST_method_not_allowed(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)

    def test_GET_not_authenticated(self):
        response = self.client.get(self.url, data={'schema': self.schema.slug})

        self.assertEqual(response.status_code, 404)

    def test_GET_not_existing_schema(self):
        self.client.login(username=self.dummy_username, password=self.dummy_password)
        response = self.client.get(self.url, data={'schema': self.schema.slug + 'not_existing'})

        self.assertEqual(response.status_code, 404)

    def test_GET_authenticated_not_owner(self):
        self.client.login(username=self.dummy_2_username, password=self.dummy_2_password)
        response = self.client.get(self.url, data={'schema': self.schema.slug})

        self.assertEqual(response.status_code, 404)

    def test_GET_correct_data(self):
        d1 = DataSet.objects.create(schema=self.schema, finished=True, file=SimpleUploadedFile('test.csv', b'123gjgh'))
        d2 = DataSet.objects.create(schema=self.schema, finished=True)
        d3 = DataSet.objects.create(schema=self.schema, finished=False)

        try:
            self.client.login(username=self.dummy_username, password=self.dummy_password)
            response = self.client.get(self.url, data={'schema': self.schema.slug})

            info = json.loads(response.content).get('info')
            for data_set_pk, data_set_info in info.items():
                data_set = DataSet.objects.get(pk=data_set_pk)
                self.assertEqual(data_set.finished, data_set_info.get('finished'))
                self.assertEqual(bool(data_set.file), data_set_info.get('file_generated'))

        finally:
            d1.file.delete()

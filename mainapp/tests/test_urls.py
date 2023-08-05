from django.test import SimpleTestCase
from django.urls import reverse, resolve

from ..views import UserLoginView, logout_user, SchemasView, CreateSchemaView, EditSchemaView, SchemaDataSets, \
    download, delete_schema, generate_data_set, get_finished_data_sets_info, UserRegisterView


class TestUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, UserRegisterView)
        
    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_user)

    def test_schema_list_url_resolves(self):
        url = reverse('schema-list')
        self.assertEqual(resolve(url).func.view_class, SchemasView)

    def test_create_schema_url_resolves(self):
        url = reverse('create-schema')
        self.assertEqual(resolve(url).func.view_class, CreateSchemaView)

    def test_edit_schema_url_resolves(self):
        url = reverse('edit-schema', kwargs={'schema_slug': 'some-slug'})
        self.assertEqual(resolve(url).func.view_class, EditSchemaView)

    def test_schema_data_sets_url_resolves(self):
        url = reverse('schema-data-sets', kwargs={'schema_slug': 'some-slug'})
        self.assertEqual(resolve(url).func.view_class, SchemaDataSets)

    def test_download_url_resolves(self):
        url = reverse('download')
        self.assertEqual(resolve(url).func, download)

    def test_delete_schema_url_resolves(self):
        url = reverse('delete-schema')
        self.assertEqual(resolve(url).func, delete_schema)

    def test_data_set_start_generating_url_resolves(self):
        url = reverse('data-set-start-generating')
        self.assertEqual(resolve(url).func, generate_data_set)

    def test_get_finished_data_sets_info_url_resolves(self):
        url = reverse('get-finished-data-sets-info')
        self.assertEqual(resolve(url).func, get_finished_data_sets_info)

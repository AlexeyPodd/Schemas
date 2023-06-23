from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve

from ..data_generators.data_generators import CellDataGenerator, RowDataGenerator
from ..models import Column, DataType, Separator, Schema
from ..views import SchemaDataSets


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_user',
            password='12345',
            email='test@mail.com',
        )

    def setUp(self):
        self.delimiter = Separator.objects.create(name='Comma', char=',')
        self.quotechar = Separator.objects.create(name='Double quote', char='\"')
        self.data_type = DataType.objects.create(name='Full Name')
        self.schema = Schema.objects.create(name='test_schema', delimiter=self.delimiter,
                                            quotechar=self.quotechar, owner=self.user)
        self.column = Column.objects.create(name='Some email', data_type=self.data_type, schema=self.schema)

    def test_upload_wrong_extention_source_file(self):
        file = SimpleUploadedFile('test.txt', b'test')
        self.data_type.source_file = file

        self.assertRaises(ValidationError, self.data_type.full_clean)

    def test_getting_cell_data_generator(self):
        data_generator = self.column.data_generator

        self.assertTrue(isinstance(data_generator, CellDataGenerator))

    def test_column_not_set_limit_for_limited_data_type(self):
        self.data_type = DataType.objects.create(name='Integer', have_limits=True)
        self.column.data_type = self.data_type
        self.column.save()

        with self.assertRaises(ValidationError):
            self.column.minimal = 12
            self.column.clean()

    def test_column_set_minimal_larger_maximum(self):
        self.data_type = DataType.objects.create(name='Integer', have_limits=True)
        self.column.data_type = self.data_type
        self.column.save()

        with self.assertRaises(ValidationError):
            self.column.maximal = 12
            self.column.minimal = 100
            self.column.clean()

    def test_schema_url(self):
        url = self.schema.get_absolute_url()

        self.assertEqual(resolve(url).func.view_class, SchemaDataSets)

    def test_getting_row_data_generator(self):
        data_generator = self.schema.data_generator

        self.assertTrue(isinstance(data_generator, RowDataGenerator))

    def test_getting_column_headers(self):
        Column.objects.create(name='second', data_type=self.data_type, schema=self.schema)
        Column.objects.create(name='third', data_type=self.data_type, schema=self.schema)
        Column.objects.create(name='forth', data_type=self.data_type, schema=self.schema)
        column_headers = self.schema.column_headers

        self.assertEqual(column_headers, [self.column.name, 'second', 'third', 'forth'])

    def test_equals_delimiter_and_qouterchar_raises_Error(self):
        with self.assertRaises(ValidationError):
            self.schema.delimiter = self.quotechar
            self.schema.clean()

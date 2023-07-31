from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import resolve

from ..data_generators.data_generators import CellDataGenerator, RowDataGenerator
from ..models import Column, Separator, Schema, SourceData
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
        self.schema = Schema.objects.create(name='test_schema', delimiter=self.delimiter,
                                            quotechar=self.quotechar, owner=self.user)
        self.column = Column.objects.create(name='Some email', data_type=Column.DataType.EMAIL, schema=self.schema)

        source_data = {
            'first_names': ['Alice', 'Bob', 'John', 'Jack', 'Piter'],
            'last_names': ["Kapahu", "Kapanke", "Kapaun", "Kapelke", "Kaper"],
            "jobs": ["3d animator", "3d artist", "3d designer", "3d modeler", "3d specialist"],
        }
        SourceData.objects.bulk_create([SourceData(source_type=s_t, source_data=s_d)
                                        for s_t, values in source_data.items() for s_d in values])

    def test_getting_cell_data_generator(self):
        data_generator = self.column.get_data_generator()

        self.assertTrue(isinstance(data_generator, CellDataGenerator))

    def test_column_data_have_limits(self):
        self.assertFalse(self.column.data_have_limits)

        self.column.data_type = Column.DataType.INTEGER
        self.column.save()

        self.assertTrue(self.column.data_have_limits)

    def test_column_get_source_data(self):
        self.column.data_type = Column.DataType.FULL_NAME
        self.column.save()

        self.assertEqual(
            self.column._get_source_data(),
            {
                'first_names': ['Alice', 'Bob', 'John', 'Jack', 'Piter'],
                'last_names': ["Kapahu", "Kapanke", "Kapaun", "Kapelke", "Kaper"],
            },
        )

    def test_column_not_set_limit_for_limited_data_type(self):
        self.column.data_type = Column.DataType.INTEGER
        self.column.save()

        with self.assertRaises(ValidationError):
            self.column.minimal = 12
            self.column.clean()

    def test_column_set_minimal_larger_maximum(self):
        self.column.data_type = Column.DataType.INTEGER
        self.column.save()

        with self.assertRaises(ValidationError):
            self.column.maximal = 12
            self.column.minimal = 100
            self.column.clean()

    def test_column_minimal_and_maximal_forcibly_set_None_if_not_having_limits(self):
        self.column.minimal = 12
        self.column.maximal = 15
        self.column.save()

        self.column.refresh_from_db()

        self.assertIsNone(self.column.minimal)
        self.assertIsNone(self.column.maximal)

    def test_schema_url(self):
        url = self.schema.get_absolute_url()

        self.assertEqual(resolve(url).func.view_class, SchemaDataSets)

    def test_getting_row_data_generator(self):
        data_generator = self.schema.get_data_generator()

        self.assertTrue(isinstance(data_generator, RowDataGenerator))

    def test_getting_column_headers(self):
        Column.objects.create(name='second', data_type=Column.DataType.EMAIL, schema=self.schema)
        Column.objects.create(name='third', data_type=Column.DataType.EMAIL, schema=self.schema)
        Column.objects.create(name='forth', data_type=Column.DataType.EMAIL, schema=self.schema)
        column_headers = self.schema.column_headers

        self.assertEqual(column_headers, [self.column.name, 'second', 'third', 'forth'])

    def test_equals_delimiter_and_qouterchar_raises_Error(self):
        with self.assertRaises(ValidationError):
            self.schema.delimiter = self.quotechar
            self.schema.clean()

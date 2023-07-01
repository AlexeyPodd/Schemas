from django.contrib.auth.models import User
from django.test import TestCase

from ..data_generators.data_generators import CellDataGenerator, RowDataGenerator
from ..models import Column, Schema, Separator


class TestDataGenerators(TestCase):
    minimal_test_value = 131
    maximal_test_value = 158

    def test_generating_cell_data(self):
        generator = CellDataGenerator(
            data_type=Column.DataType.INTEGER,
            have_limits=True,
            minimal=self.minimal_test_value,
            maximal=self.maximal_test_value,
        )

        for _ in range(1000):
            data = generator()

            self.assertTrue(self.minimal_test_value <= int(data) <= self.maximal_test_value)

    def test_generating_row_data(self):
        user = User.objects.create_user(
            username='dummy_test_user',
            password='32145',
            email='dummy@gmail.com',
        )
        delimiter = Separator.objects.create(name='dot', char='.')
        quotechar = Separator.objects.create(name='double-quote', char='"')
        schema = Schema.objects.create(
            name="test_schema",
            owner=user,
            delimiter=delimiter,
            quotechar=quotechar,
        )
        columns = Column.objects.bulk_create([
            Column(name='Name', data_type=Column.DataType.FULL_NAME, schema=schema, order=1),
            Column(name='Age', data_type=Column.DataType.INTEGER, minimal=self.minimal_test_value,
                   maximal=self.maximal_test_value, schema=schema, order=2),
            Column(name='Address of Living', data_type=Column.DataType.ADDRESS, schema=schema, order=3),
            Column(name='E-mail', data_type=Column.DataType.EMAIL, schema=schema, order=4),
            Column(name='Job', data_type=Column.DataType.JOB, schema=schema, order=5),
        ])
        column_names = set(column.name for column in columns)

        generator = RowDataGenerator(columns)

        for _ in range(1000):
            data = generator()

            self.assertTrue(isinstance(data, dict))
            self.assertEqual(set(data.keys()), column_names)
            self.assertTrue(all(map(lambda v: isinstance(v, str), data.values())))
            self.assertTrue(all(data.values()))

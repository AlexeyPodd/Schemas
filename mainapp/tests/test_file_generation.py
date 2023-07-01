import csv
import os
import re

from django.contrib.auth.models import User
from django.test import TestCase

from ..data_generators.file_generation import generate_csv_file
from ..models import Separator, Schema, Column, DataSet


class TestGenerateCSVFile(TestCase):
    dummy_username = 'dummy_test_user'
    dummy_password = '32145'
    dummy_email = 'dummy@gmail.com'

    schema_name = 'test_schema'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username=cls.dummy_username,
            password=cls.dummy_password,
            email=cls.dummy_email,
        )

        cls.delimiter = Separator.objects.create(name='dot', char='.')
        cls.quotechar = Separator.objects.create(name='double-quote', char='"')

        cls.schema = Schema.objects.create(
            name=cls.schema_name,
            owner=cls.user,
            delimiter=cls.delimiter,
            quotechar=cls.quotechar,
        )

        cls.column_1 = Column.objects.create(
            name='first_column_signal_test',
            minimal=1,
            maximal=10,
            data_type=Column.DataType.INTEGER,
            schema=cls.schema,
        )
        cls.column_2 = Column.objects.create(
            name='second_column_signal_test',
            minimal=2,
            maximal=8,
            data_type=Column.DataType.FULL_NAME,
            schema=cls.schema,
            order=2,
        )

    def test_file_generating(self):
        data_set = DataSet.objects.create(schema=self.schema)
        integer_regex = re.compile(r'\d{1,10}')
        full_name_regex = re.compile(r'[A-Z][a-z]+(?:[ -][A-Z][a-z]+)? [A-Z][a-z]+')

        generate_csv_file(data_set=data_set, rows_amount=1000)

        self.assertTrue(data_set.finished)
        self.assertTrue(data_set.file)

        try:
            with open(os.path.abspath(data_set.file.path), newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=self.delimiter.char, quotechar=self.quotechar.char)
                for row in reader:
                    integer = row[self.column_1.name]
                    full_name = row[self.column_2.name]

                    self.assertTrue(re.fullmatch(integer_regex, integer))
                    self.assertTrue(re.fullmatch(full_name_regex, full_name))

        except:
            self.fail("invalid file")
        finally:
            data_set.file.delete()

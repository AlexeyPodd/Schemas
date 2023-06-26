import csv
import os
import re

from django.contrib.auth.models import User
from django.test import TestCase

from schemas.settings import MEDIA_ROOT
from ..data_generators.file_generation import generate_csv_file
from ..models import Separator, Schema, Column, DataType, DataSet


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
            name='first_column_signal_test',
            minimal=1,
            maximal=10,
            data_type=cls.data_type_1,
            schema=cls.schema,
        )
        cls.column_2 = Column.objects.create(
            name='second_column_signal_test',
            minimal=2,
            maximal=8,
            data_type=cls.data_type_2,
            schema=cls.schema,
            order=2,
        )

    def test_file_generating(self):
        data_set = DataSet.objects.create(schema=self.schema)
        word_regex = re.compile(r'[a-z]{1,10}')
        sentensce_regex = re.compile(r'[A-Z][a-z]{2,9}(?: [a-z]{3,10}){1,7}\.')

        generate_csv_file(data_set=data_set, rows_amount=200)

        self.assertTrue(data_set.finished)
        self.assertTrue(data_set.file)

        try:
            with open(os.path.abspath(data_set.file.path), newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=self.delimiter.char, quotechar=self.quotechar.char)
                for row in reader:
                    word = row['first_column_signal_test']
                    sentence = row['second_column_signal_test']
                    self.assertTrue(re.fullmatch(word_regex, word))
                    self.assertTrue(re.fullmatch(sentensce_regex, sentence))

        except:
            self.fail("invalid file")
        finally:
            data_set.file.delete()

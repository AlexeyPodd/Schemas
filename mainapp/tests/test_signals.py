import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from mainapp.models import Separator, Schema, DataSet


class TestSignals(TestCase):
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

    def tearDown(self):
        if hasattr(self, 'saved_path') and os.path.isfile(self.saved_path):
            os.remove(self.saved_path)

    def test_data_set_file_deleting_signal(self):
        test_scv_file = SimpleUploadedFile('test.csv', b'123gjgh')
        data_set = DataSet.objects.create(schema=self.schema, file=test_scv_file)
        self.saved_path = os.path.abspath(data_set.file.path)

        self.assertTrue(os.path.isfile(self.saved_path))

        data_set.delete()

        self.assertFalse(os.path.isfile(self.saved_path))

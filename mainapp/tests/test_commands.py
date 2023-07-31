from io import StringIO
from unittest import TestCase
from django.core.management import call_command

from mainapp.models import SourceData


class TestDataGenerators(TestCase):
    def tearDown(self):
        SourceData.objects.all().delete()

    def test_load_data_source_correct_work(self):
        out = StringIO()
        call_command('load_data_source', 'static/source/test.json', stdout=out)
        self.assertEqual(SourceData.objects.count(), 3)

    def test_load_data_source_not_existing_file(self):
        out = StringIO()
        with self.assertRaises(FileNotFoundError):
            call_command('load_data_source', 'static/source/testststst.json', stdout=out)
        self.assertEqual(SourceData.objects.count(), 0)

    def test_load_data_source_force_rewrite(self):
        out = StringIO()
        SourceData.objects.create(source_type='letters', source_data='q')
        SourceData.objects.create(source_type='letters', source_data='w')
        SourceData.objects.create(source_type='letters', source_data='e')

        call_command('load_data_source', 'static/source/test.json', force=True, stdout=out)
        self.assertEqual(SourceData.objects.count(), 3)

    def test_load_data_source_multiple_files(self):
        out = StringIO()
        call_command('load_data_source', 'static/source/test.json', 'static/source/test2.json', stdout=out)
        self.assertEqual(SourceData.objects.count(), 6)

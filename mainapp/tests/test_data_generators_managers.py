import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..data_generators.managers import GenerationManager
from ..models import DataType


class TestGenerationManager(TestCase):
    def tearDown(self):
        if hasattr(self, 'data_type'):
            self.data_type.delete()

    def test_get_generation_method_returns_right_generation_function(self):
        data_type_name = 'Word'

        func = GenerationManager.get_generation_method(data_type_name)

        self.assertTrue(callable(func))
        self.assertEqual(func.__name__, 'generate_word')

    def test_get_generation_kwargs_returns_kwargs_dict(self):
        self.data_type = DataType.objects.create(
            name='Word',
            have_limits=True,
            source_file=SimpleUploadedFile('test.json', json.dumps({'letters': ['a', 'b', 'c']}).encode())
        )

        kwargs = GenerationManager.get_generation_kwargs(
            have_limits=self.data_type.have_limits,
            minimal=0,
            maximal=10,
            source_file=self.data_type.source_file,
        )

        self.assertTrue(isinstance(kwargs, dict))
        self.assertEqual(kwargs.get('minimal'), 0)
        self.assertEqual(kwargs.get('maximal'), 10)
        self.assertEqual(kwargs.get('letters'), ['a', 'b', 'c'])
        self.assertEqual(len(kwargs), 3)

    def test_get_generation_kwargs_need_limits_but_not_passed(self):
        self.data_type = DataType.objects.create(
            name='Word',
            have_limits=True,
            source_file=SimpleUploadedFile('test.json', json.dumps({'letters': ['a', 'b', 'c']}).encode()))

        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=self.data_type.have_limits,
                minimal=0,
                maximal=None,
                source_file=self.data_type.source_file,
            )
        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=self.data_type.have_limits,
                minimal=None,
                maximal=10,
                source_file=self.data_type.source_file,
            )
        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=self.data_type.have_limits,
                minimal=None,
                maximal=None,
                source_file=self.data_type.source_file,
            )

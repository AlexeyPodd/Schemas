from django.test import TestCase

from ..data_generators.managers import GenerationManager


class TestGenerationManager(TestCase):
    def tearDown(self):
        if hasattr(self, 'data_type') and self.data_type.source_file:
            self.data_type.source_file.delete()

    def test_get_generation_method_returns_right_generation_function(self):
        data_type_name = 'Word'

        func = GenerationManager.get_generation_method(data_type_name)

        self.assertTrue(callable(func))
        self.assertEqual(func.__name__, 'generate_word')

    def test_get_generation_kwargs_returns_kwargs_dict(self):
        kwargs = GenerationManager.get_generation_kwargs(
            have_limits=True,
            minimal=0,
            maximal=10,
            source_file_name="test.json",
        )

        self.assertTrue(isinstance(kwargs, dict))
        self.assertEqual(kwargs.get('minimal'), 0)
        self.assertEqual(kwargs.get('maximal'), 10)
        self.assertEqual(kwargs.get('letters'), ['a', 'b', 'c'])
        self.assertEqual(len(kwargs), 3)

    def test_get_generation_kwargs_returns_empty_dict_if_limits_and_file_are_not_needed(self):
        kwargs = GenerationManager.get_generation_kwargs(
            have_limits=False,
            minimal=0,
            maximal=10,
            source_file_name=None,
        )

        self.assertTrue(isinstance(kwargs, dict))
        self.assertEqual(len(kwargs), 0)

    def test_get_generation_kwargs_need_limits_but_not_passed(self):
        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=True,
                minimal=0,
                maximal=None,
                source_file_name="test.json",
            )
        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=True,
                minimal=None,
                maximal=10,
                source_file_name="test.json",
            )
        with self.assertRaises(ValueError):
            GenerationManager.get_generation_kwargs(
                have_limits=True,
                minimal=None,
                maximal=None,
                source_file_name="test.json",
            )

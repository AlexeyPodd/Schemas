import json
from typing import Callable

from django.db.models.fields.files import FieldFile
from django.utils.text import slugify

from . import data_generation


class GenerationManager:
    @staticmethod
    def get_generation_method(data_type_name: str) -> Callable:
        method_name = 'generate_' + slugify(data_type_name).replace('-', '_')
        generation_method = getattr(data_generation, method_name)
        if generation_method is None:
            raise AttributeError(f"Data generator with name {method_name} was not found")
        return generation_method

    @classmethod
    def get_generation_kwargs(cls, have_limits: bool, minimal: [int, None], maximal: [int, None],
                              source_file: [FieldFile, None]) -> dict:

        if have_limits and (minimal is None or maximal is None):
            raise ValueError("Both limits (maximal and minimal) nust be set")

        kwargs = {}
        if have_limits:
            kwargs.update(dict(minimal=minimal, maximal=maximal))

        if source_file:
            kwargs.update(cls._read_source_file(source_file))
        return kwargs

    @staticmethod
    def _read_source_file(file: FieldFile) -> dict:
        try:
            f = file.open('r')
            data = json.load(f)
            if not isinstance(data, dict):
                raise TypeError("The content of the source file must be a dictionary")
        except FileNotFoundError:
            raise ValueError("Data type contains invalid path to source file")
        except Exception:
            raise ValueError("Source file contains invalid data")
        return data

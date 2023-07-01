import json
import os
from typing import Callable

from schemas.settings import STATIC_ROOT
from . import data_generation


class GenerationManager:
    @staticmethod
    def get_generation_method(data_type_name: str) -> Callable:
        method_name = 'generate_' + data_type_name.lower()
        generation_method = getattr(data_generation, method_name)
        if generation_method is None:
            raise AttributeError(f"Data generator with name {method_name} was not found")
        return generation_method

    @classmethod
    def get_generation_kwargs(cls, have_limits: bool, minimal: [int, None], maximal: [int, None],
                              source_file_name: [str, None]) -> dict:

        if have_limits and (minimal is None or maximal is None):
            raise ValueError("Both limits (maximal and minimal) nust be set")

        kwargs = {}
        if have_limits:
            kwargs.update(dict(minimal=minimal, maximal=maximal))

        if source_file_name:
            kwargs.update(cls._read_source_file(source_file_name))
        return kwargs

    @staticmethod
    def _read_source_file(file_name: str) -> dict:
        try:
            with open(os.path.join(STATIC_ROOT, 'source', file_name)) as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise TypeError("The content of the source file must be a dictionary")
        except FileNotFoundError:
            raise ValueError("Data type contains invalid path to source file")
        except Exception:
            raise ValueError("Source file contains invalid data")
        return data

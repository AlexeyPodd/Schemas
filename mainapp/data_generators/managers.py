from typing import Callable

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
                              source_data: [dict, None]) -> dict:

        if have_limits and (minimal is None or maximal is None):
            raise ValueError("Both limits (maximal and minimal) nust be set")

        kwargs = {}
        if have_limits:
            kwargs.update(dict(minimal=minimal, maximal=maximal))

        if source_data:
            kwargs.update(source_data)

        return kwargs

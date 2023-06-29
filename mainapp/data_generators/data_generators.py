from .managers import GenerationManager


class CellDataGenerator:
    """Class for generating data of cell based on column's type and limitations, if needed"""
    def __init__(self, data_type, minimal=None, maximal=None):
        self._generation_method = GenerationManager.get_generation_method(data_type.name)
        self._generation_kwargs = GenerationManager.get_generation_kwargs(have_limits=data_type.have_limits,
                                                                          minimal=minimal,
                                                                          maximal=maximal,
                                                                          source_file=data_type.source_file)

    def __call__(self):
        return self._generation_method(**self._generation_kwargs)


class RowDataGenerator:
    """Class for generating data of one row in schema, in dict format {column_name: value_in_this_row}"""
    def __init__(self, schema_columns):
        self._cell_generators = {column.name: column.get_data_generator() for column in schema_columns}

    def __call__(self):
        return {field_name: gen() for field_name, gen in self._cell_generators.items()}

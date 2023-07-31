import json
from typing import List

from django.core.management import BaseCommand

from ...models import SourceData


class Command(BaseCommand):
    help = "Command for load source data for generating data, that need source, from json file to db."

    def add_arguments(self, parser):
        parser.add_argument("file_names", nargs="+", type=str, help="Paths to source files.")
        parser.add_argument("-f", "--force", action="store_true",
                            help="Rewrite source data for types, stored in this files, "
                                 "even if it already exists in db.")

    def handle(self, *args, **options):
        file_names = options['file_names']
        force = options['force']

        for file_name in file_names:
            if not file_name.endswith('.json'):
                self.stdout.write(f"Only json files are acceptable, not {file_name}.")
                return

        for file_name in file_names:
            self._write_data_from_json_file_to_db(file_name, force)

    def _write_data_from_json_file_to_db(self, filename, force):
        with open(filename) as file:
            data = json.load(file)

        for source_type, values in data.items():
            self.stdout.write(f"loading {source_type} to db...")
            self._load_source_data_for_type(source_type, values, force)
            self.stdout.write(f"loading {source_type} to db was finished.")

    def _load_source_data_for_type(self, source_type: str, values: List[str], force: bool):
        if not values:
            raise ValueError("No values for inserting.")

        if not isinstance(values, list) or not all(map(lambda v: isinstance(v, str), values)):
            raise TypeError("Values must be list of strings.")

        if SourceData.objects.filter(source_type=source_type).exists():
            if force:
                SourceData.objects.filter(source_type=source_type).delete()
            else:
                self.stdout.write(f"Source data of type {source_type} already exists in db."
                                  f" If you want to rewrite it use option --force.")
                return

        source_data_instances = [SourceData(source_type=source_type, source_data=value) for value in values]
        SourceData.objects.bulk_create(source_data_instances)

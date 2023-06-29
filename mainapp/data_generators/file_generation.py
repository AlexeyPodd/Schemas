import csv
import os

from schemas.settings import MEDIA_ROOT


def generate_csv_file(data_set, rows_amount: int) -> None:
    # Generating uniq filename
    filename = f'{data_set.schema.name}_data_set.csv'
    i = 1
    while os.path.isfile(os.path.abspath(os.path.join(MEDIA_ROOT, 'csv_files', filename))):
        filename = f'{data_set.schema.name}_data_set({i}).csv'
        i += 1
    path = os.path.join('csv_files', filename)
    absolute_path = os.path.abspath(os.path.join(MEDIA_ROOT, 'csv_files', filename))

    try:
        # Generating file
        with open(absolute_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=data_set.schema.column_headers,
                delimiter=data_set.schema.delimiter.char,
                quotechar=data_set.schema.quotechar.char,
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()

            data_generator = data_set.schema.get_data_generator()
            for _ in range(rows_amount):
                writer.writerow(data_generator())
    except:
        # Deleting file from file system, if failed to write content in it
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
    else:
        # Setting new file ti FileField of Data Set
        data_set.file.name = path
    finally:
        # Writing to db that file generating process is finished
        data_set.finished = True
        data_set.save()

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth.models import User

from .data_generators.data_generators import CellDataGenerator, RowDataGenerator
from .data_generators.file_generation import generate_csv_file


class Column(models.Model):
    """
    Represents column in schema.

    If you want to add new type of data for generating, you should:
        1. Add name of data type and short version of name (3 chars) to inner class DataType, likewise present.
        2. Add function for generating data to file data_generation.py in package data_generators.
            2.1 If your data type have limits (minimal and maximal), function should take these parameters.
            2.2 If your data type uses source data for generating - function should take this source data lists as
            arguments, named as source data types.
        3. If your data type have limits, you also should add it to LIMITED_DATA_TYPES collection below.
        4. If your data type uses source data, you also should:
            4.1 Add it to DATA_TYPE_SOURCE_TYPES dictionary below as key, with value of list with source data types.
            4.2 Add this data to data base via model SourceData using one of methods - manage.py shell,
                admin of the site, or load from json file using command "load_data_source" (in this case json file must
                contain dictionary, where keys are source data types,
                and values are lists of data options for generating).

    """

    class DataType(models.TextChoices):
        INTEGER = "INT"
        FULL_NAME = "FNM"
        JOB = "JOB"
        EMAIL = "EML"
        DOMAIN_NAME = "DMN"
        PHONE_NUMBER = "PHN"
        COMPANY_NAME = "CMN"
        TEXT = "TXT"
        ADDRESS = "ADR"
        DATE = "DTE"

    LIMITED_DATA_TYPES = (DataType.INTEGER, DataType.TEXT)
    DATA_TYPE_SOURCE_TYPES = {DataType.FULL_NAME: ["first_names", "last_names"], DataType.JOB: ["jobs"]}

    name = models.CharField(max_length=64)
    minimal = models.PositiveSmallIntegerField(blank=True, null=True)
    maximal = models.PositiveSmallIntegerField(blank=True, null=True)
    data_type = models.CharField(max_length=3, choices=DataType.choices)
    schema = models.ForeignKey('Schema', on_delete=models.CASCADE, related_name='columns')
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Schema column'
        verbose_name_plural = 'Schema columns'
        ordering = ['schema', 'order']

    def __str__(self):
        return self.name

    @property
    def data_have_limits(self):
        return self.data_type in self.LIMITED_DATA_TYPES

    def _get_source_data(self):
        source_types = self.DATA_TYPE_SOURCE_TYPES.get(self.data_type)
        data = {}

        if source_types is not None:
            for source_type in source_types:
                source_data_list = list(
                    SourceData.objects.filter(source_type=source_type).values_list('source_data', flat=True),
                )

                if not source_data_list:
                    raise ObjectDoesNotExist(f"Not Found Source Data with type {source_type}.")

                data.update(
                    {source_type: source_data_list},
                )

        return data

    def get_data_generator(self):
        return CellDataGenerator(
            data_type=self.DataType(self.data_type),
            have_limits=self.data_have_limits,
            minimal=self.minimal,
            maximal=self.maximal,
            source_data=self._get_source_data(),
        )

    def clean(self):
        if self.data_type in self.LIMITED_DATA_TYPES:

            if self.minimal is None or self.maximal is None:
                raise ValidationError('Limits (From and To) should both be set for this Type of column')

            if self.minimal > self.maximal:
                raise ValidationError('From should be less number then To, or equal')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.data_have_limits:
            self.minimal = None
            self.maximal = None
        super().save()


class SourceData(models.Model):
    """Model for storing source data for generating data types, that needs source."""
    source_type = models.CharField(max_length=25, db_index=True)
    source_data = models.CharField(max_length=60)


class Schema(models.Model):
    """Represent schema, the structure of generating data sets."""
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from='name', unique=True)
    time_update = models.DateField(auto_now=True, verbose_name='modified')
    delimiter = models.ForeignKey('Separator', on_delete=models.PROTECT, related_name='schemas_with_delimiter')
    quotechar = models.ForeignKey('Separator', on_delete=models.PROTECT, related_name='schemas_with_quotechar')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schemas')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('schema-data-sets', kwargs={'schema_slug': self.slug})

    def get_data_generator(self):
        return RowDataGenerator(self.columns.all())

    @property
    def column_headers(self):
        return list(map(lambda d: d['name'], self.columns.values('name')))

    def clean(self):
        # hasattr needs to avoid error, which occurs when empty data is transferred to ModelForm while testing
        if hasattr(self, 'delimiter') and hasattr(self, 'quotechar') and self.delimiter == self.quotechar:
            raise ValidationError('String character must not be the same as column separator')


class Separator(models.Model):
    """Model of separator (delimiter and quotechar) in generating csv files."""
    name = models.CharField(max_length=32)
    char = models.CharField(max_length=1, unique=True)

    def __str__(self):
        return f"{self.name} ({self.char})"


class DataSet(models.Model):
    """
    Representation of data set.
    If generating of csv file is processing: finished status is False, and it links to no file.
    If file generating was successful: finished status would be True and field 'file' contains link to csv file.
    If file generating fails: finished status would be True, but field 'file' links to no file.
    """
    time_create = models.DateField(auto_now_add=True, verbose_name="created")
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])], blank=True,
                            verbose_name='csv file')
    schema = models.ForeignKey('Schema', on_delete=models.CASCADE, related_name='data_sets')
    finished = models.BooleanField(default=False, verbose_name='generating csv file is finished')

    class Meta:
        verbose_name = 'Data set'
        verbose_name_plural = 'Data sets'
        ordering = ['time_create']

    def generate_file(self, rows_amount):
        generate_csv_file(self, rows_amount=rows_amount)

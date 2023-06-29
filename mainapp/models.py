from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth.models import User

from .data_generators.data_generators import CellDataGenerator, RowDataGenerator
from .data_generators.file_generation import generate_csv_file
from .utils import get_source_file_path


class DataType(models.Model):
    """
    For every object must be function for generating corresponding data in data_generators.generation.
    If this function need source file - it should be uploaded by admin, while creating instance of model.
    """

    name = models.CharField(max_length=32, unique=True)
    have_limits = models.BooleanField(default=False, verbose_name='have limits')
    source_file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['json'])], blank=True,
                                   upload_to=get_source_file_path, verbose_name='source file')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Data type'
        verbose_name_plural = 'Data types'


class Column(models.Model):
    name = models.CharField(max_length=64)
    minimal = models.PositiveSmallIntegerField(blank=True, null=True)
    maximal = models.PositiveSmallIntegerField(blank=True, null=True)
    data_type = models.ForeignKey('DataType', on_delete=models.PROTECT, related_name='columns', verbose_name='type')
    schema = models.ForeignKey('Schema', on_delete=models.CASCADE, related_name='columns')
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Schema column'
        verbose_name_plural = 'Schema columns'
        ordering = ['schema', 'order']

    def __str__(self):
        return self.name

    def get_data_generator(self):
        return CellDataGenerator(
            data_type=self.data_type,
            minimal=self.minimal,
            maximal=self.maximal,
        )

    def clean(self):
        # hasattr needs to avoid error, which occurs when empty data is transferred to InlineFormSet
        if hasattr(self, 'data_type') and self.data_type.have_limits:

            if self.minimal is None or self.maximal is None:
                raise ValidationError('Limits (From and To) should both be set for this Type of column')

            if self.minimal > self.maximal:
                raise ValidationError('From should be less number then To , or equal')


class Schema(models.Model):
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
        # hasattr needs to avoid error, which occurs when empty data is transferred to ModelForm
        if hasattr(self, 'delimiter') and hasattr(self, 'quotechar') and self.delimiter == self.quotechar:
            raise ValidationError('String character must not be the same as column separator')


class Separator(models.Model):
    name = models.CharField(max_length=32)
    char = models.CharField(max_length=1, unique=True)

    def __str__(self):
        return f"{self.name} ({self.char})"


class DataSet(models.Model):
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

# Generated by Django 4.1.3 on 2023-06-23 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_alter_dataset_file_alter_datatype_source_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='maximal',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='column',
            name='minimal',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
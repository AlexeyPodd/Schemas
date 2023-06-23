from django.contrib import admin

from .forms import SeparatorForm


class DataTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'have_limits', 'source_file')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('have_limits',)


class SeparatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'char')
    list_editable = ('name', 'char')
    fields = ('name', 'char')
    form = SeparatorForm


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'minimal', 'maximal', 'data_type', 'schema')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('schema__owner', 'data_type', 'schema')
    fields = ('name', 'minimal', 'maximal', 'data_type', 'schema')


class SchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'time_update', 'delimiter', 'quotechar', 'owner',
                    'get_generated_data_sets_amount')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'owner')
    list_filter = ('delimiter', 'quotechar', 'time_update')
    fields = ('name', 'slug', 'time_update', 'delimiter', 'quotechar', 'owner', 'get_generated_data_sets_amount')
    readonly_fields = ('slug', 'time_update', 'get_generated_data_sets_amount')

    def get_generated_data_sets_amount(self, obj):
        return obj.data_sets.count()

    get_generated_data_sets_amount.short_description = "Generated Data Sets"


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'time_create', 'file', 'finished')
    list_display_links = ('id',)
    search_fields = ('schema', 'schema__owner')
    list_filter = ('time_create', 'finished')
    fields = ('schema', 'schema__owner', 'time_create', 'file', 'finished')
    readonly_fields = ('schema', 'time_create', 'file', 'finished')

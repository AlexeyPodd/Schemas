from django.contrib import admin

from .admin_models import ColumnAdmin, SeparatorAdmin, SchemaAdmin, DataSetAdmin
from .models import Column, Separator, Schema, DataSet


admin.site.register(Column, ColumnAdmin)
admin.site.register(Separator, SeparatorAdmin)
admin.site.register(Schema, SchemaAdmin)
admin.site.register(DataSet, DataSetAdmin)

admin.site.site_title = "FakeCSV - Administration"
admin.site.site_header = "FakeCSV site administration"

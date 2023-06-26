from django.urls import path

from mainapp.views import UserLoginView, logout_user, SchemasView, CreateSchemaView, EditSchemaView, SchemaDataSets,\
    download, delete_schema, generate_data_set, get_finished_data_sets_info

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('', SchemasView.as_view(), name='schema-list'),
    path('create-schema/', CreateSchemaView.as_view(), name='create-schema'),
    path('edit/<slug:schema_slug>/', EditSchemaView.as_view(), name='edit-schema'),
    path('data-sets/<slug:schema_slug>/', SchemaDataSets.as_view(), name='schema-data-sets'),
    path('download/', download, name='download'),
    path('delete-schema/', delete_schema, name='delete-schema'),
    path('start-generating/', generate_data_set, name='data-set-start-generating'),
    path('get-finished-data-sets-info/', get_finished_data_sets_info, name='get-finished-data-sets-info'),
]

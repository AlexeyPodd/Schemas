from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import ExpressionWrapper, Q, BooleanField
from django.http import HttpResponseRedirect, Http404, FileResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from .base_views import base_view_for_ajax
from .forms import RegisterUserForm, LoginUserForm, SchemaForm, ColumnFormSet
from .models import Schema, DataSet, Column


class UserRegisterView(CreateView):
    """View for registering new user."""
    form_class = RegisterUserForm
    template_name = 'mainapp/auth_form.html'
    extra_context = {'title': 'Registration',
                     'button_label': 'Register'}

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('schema-list')


class UserLoginView(LoginView):
    """View for login page."""
    form_class = LoginUserForm
    template_name = 'mainapp/auth_form.html'
    extra_context = {'title': 'Login',
                     'button_label': 'Login'}

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        return reverse_lazy('schema-list')


def logout_user(request):
    logout(request)
    return redirect('login')


class SchemasView(LoginRequiredMixin, ListView):
    """View for page with user's schemas."""
    model = Schema
    template_name = 'mainapp/schemas.html'
    context_object_name = 'schemas'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Data Schemas',
            'current_section': 'schemas',
            'schema_slugs': [schema.slug for schema in context[self.context_object_name]],
        })
        return context


class CreateSchemaView(LoginRequiredMixin, CreateView):
    """View for page with form, where user can create new schema."""
    model = Schema
    template_name = 'mainapp/schema_form.html'
    form_class = SchemaForm
    formset_class = ColumnFormSet

    def get(self, request, *args, **kwargs):
        self.formset = self.formset_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        self.formset = self.formset_class(self.request.POST)
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.owner_id = self.request.user.pk
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_types_need_limits = Column.LIMITED_DATA_TYPES
        context.update({
            'title': 'New schema',
            'formset': self.formset,
            'data_types_need_limits': data_types_need_limits,
        })
        return context


class EditSchemaView(LoginRequiredMixin, UpdateView):
    """Page with form, where user can edit one of his schemas."""
    model = Schema
    template_name = 'mainapp/schema_form.html'
    form_class = SchemaForm
    formset_class = ColumnFormSet
    slug_url_kwarg = 'schema_slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.select_related('owner'))
        if self.object.owner != request.user:
            raise Http404

        self.formset = self.formset_class(instance=self.object)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.select_related('owner'))
        if self.object.owner != request.user:
            raise Http404

        form = self.get_form()
        self.formset = self.formset_class(self.request.POST, instance=self.object)

        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.formset.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_types_need_limits = Column.LIMITED_DATA_TYPES
        context.update({
            'title': 'Edit schema',
            'formset': self.formset,
            'data_types_need_limits': data_types_need_limits,
        })
        return context


class SchemaDataSets(LoginRequiredMixin, SingleObjectMixin, ListView):
    """
    View for page with list of previously generated data sets of specific schema.
    Also on this page user can generate new data sets of this schema, download generated schemas or delete them.
    """
    template_name = 'mainapp/schema_data_sets.html'
    slug_url_kwarg = 'schema_slug'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Schema.objects.prefetch_related('columns').select_related('owner'),
            slug=kwargs[self.slug_url_kwarg],
        )
        if self.object.owner != request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.data_sets.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update({
            'title': 'Data sets',
            'schema': self.object,
        })
        return context


@require_GET
@login_required
def download(request):
    """View for processing downloads generated data sets."""
    data_set = get_object_or_404(DataSet.objects.select_related('schema__owner'), pk=request.GET.get('data_set'))
    if data_set.schema.owner != request.user:
        raise Http404

    if not data_set.file:
        raise Http404

    return FileResponse(data_set.file.open(), as_attachment=True, filename=data_set.file.name)


@base_view_for_ajax(allowed_method='POST')
def delete_schema(request, schema):
    """View for deletion data set on ajax request."""
    schema_slug = schema.slug
    schema.delete()
    return JsonResponse({'deleted_schema': schema_slug})


@base_view_for_ajax(allowed_method='POST')
def generate_data_set(request, schema):
    """View for generating new data set on ajax request."""
    try:
        rows_amount = int(request.POST.get('rows'))
    except (TypeError, ValueError):
        return JsonResponse({'file_generated': False}, status=400)

    if rows_amount < 1:
        return JsonResponse({'file_generated': False}, status=400)

    data_set = DataSet.objects.create(schema=schema)
    data_set.generate_file(rows_amount)
    return JsonResponse({'file_generated': bool(data_set.file), 'data_set_id': data_set.pk})


@base_view_for_ajax(allowed_method='GET')
def get_finished_data_sets_info(request, schema):
    """
    View for monitoring current statuses of generating data sets.
    Needs if user disconnected from server and then connects again before generation of file ended.
    """
    data_sets = DataSet.objects.filter(schema=schema).\
        annotate(file_generated=ExpressionWrapper(~Q(file=''), output_field=BooleanField())).\
        values('id', 'finished', 'file_generated')

    info = {data_set['id']: {'file_generated': data_set['file_generated']}
            for data_set in data_sets if data_set['finished']}

    return JsonResponse({'info': info})

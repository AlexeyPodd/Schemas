from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ExpressionWrapper, Q, BooleanField
from django.http import HttpResponseRedirect, Http404, HttpResponse, FileResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from .forms import LoginUserForm, SchemaForm, ColumnFormSet
from .models import Schema, DataSet, DataType, Column


class UserLoginView(LoginView):
    form_class = LoginUserForm
    template_name = 'mainapp/login.html'
    extra_context = {'title': 'Login',
                     'button_label': 'Login'}

    def get_success_url(self):
        next = self.request.GET.get('next')
        if next:
            return next

        return reverse_lazy('schema-list')


def logout_user(request):
    logout(request)
    return redirect('login')


class SchemasView(LoginRequiredMixin, ListView):
    model = Schema
    template_name = 'mainapp/schemas.html'
    context_object_name = 'schemas'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Data Schemas',
            'current_section': 'schemas',
        })
        return context

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)


class CreateSchemaView(LoginRequiredMixin, CreateView):
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
        data_types_need_limits = [i for i, data_type in enumerate(DataType.objects.all(), 1) if data_type.have_limits]
        context.update({
            'title': 'New schema',
            'formset': self.formset,
            'data_types_need_limits': data_types_need_limits,
        })
        return context


class EditSchemaView(LoginRequiredMixin, UpdateView):
    model = Schema
    template_name = 'mainapp/schema_form.html'
    form_class = SchemaForm
    formset_class = ColumnFormSet
    slug_url_kwarg = 'schema_slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.select_related('owner'))
        if self.object.owner != request.user:
            raise Http404

        self.formset = self.formset_class(
            instance=self.object,
            queryset=Column.objects.select_related('data_type').filter(schema=self.object),
        )
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.select_related('owner'))
        if self.object.owner != request.user:
            raise Http404

        form = self.get_form()
        self.formset = self.formset_class(
            self.request.POST,
            instance=self.object,
            queryset=Column.objects.select_related('data_type').filter(schema=self.object),
        )

        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.formset.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_types_need_limits = [i for i, data_type in enumerate(DataType.objects.all(), 1) if data_type.have_limits]
        context.update({
            'title': 'Edit schema',
            'formset': self.formset,
            'data_types_need_limits': data_types_need_limits,
        })
        return context


class SchemaDataSets(LoginRequiredMixin, SingleObjectMixin, ListView):
    template_name = 'mainapp/schema_data_sets.html'
    slug_url_kwarg = 'schema_slug'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Schema.objects.prefetch_related('columns__data_type').select_related('owner'),
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


@login_required
def download(request):
    if request.method != 'GET':
        return HttpResponse(status=405)

    data_set = get_object_or_404(DataSet, pk=request.GET.get('data_set'))
    if data_set.schema.owner != request.user:
        raise Http404

    if not data_set.file:
        raise Http404

    return FileResponse(data_set.file.open(), as_attachment=True, filename=data_set.file.name)


def delete_schema(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    schema_slug = request.POST.get('schema')
    try:
        schema = Schema.objects.select_related('owner').get(slug=schema_slug, owner=request.user)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    if schema.owner != request.user:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    schema.delete()
    return JsonResponse({'deleted_schema': schema_slug})


def generate_data_set(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    try:
        schema = Schema.objects.select_related('owner').get(slug=request.POST.get('schema'))
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    if schema.owner != request.user:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    try:
        rows_amount = int(request.POST.get('rows'))
    except (TypeError, ValueError):
        return JsonResponse({'file_generated': False}, status=400)

    if rows_amount < 1:
        return JsonResponse({'file_generated': False}, status=400)

    data_set = DataSet.objects.create(schema=schema)
    data_set.generate_file(rows_amount)
    return JsonResponse({'file_generated': bool(data_set.file), 'data_set_id': data_set.pk})


def get_finished_data_sets_info(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    try:
        schema = Schema.objects.select_related('owner').get(slug=request.GET.get('schema'), owner=request.user)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    if schema.owner != request.user:
        return JsonResponse({'error': 'Not Founded'}, status=404)

    data_sets = DataSet.objects.filter(schema=schema).\
        annotate(file_generated=ExpressionWrapper(~Q(file=''), output_field=BooleanField())).\
        values('id', 'finished', 'file_generated')

    info = {data_set['id']: {'file_generated': data_set['file_generated']}
            for data_set in data_sets if data_set['finished']}

    return JsonResponse({'info': info})

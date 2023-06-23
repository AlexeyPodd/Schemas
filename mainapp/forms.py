from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError

from mainapp.models import Schema, Column, Separator


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'name'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'password'}))


class SeparatorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For ability to set space char
        self.fields['char'].strip = False

    class Meta:
        model = Separator
        fields = "__all__"


class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ['name', 'delimiter', 'quotechar']
        labels = {
            'name': 'Name',
            'delimiter': 'Column separator',
            'quotechar': 'String character',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'delimiter': forms.Select(attrs={'class': 'form-select'}),
            'quotechar': forms.Select(attrs={'class': 'form-select'}),
        }


class BaseColumnInlineFormSet(forms.BaseInlineFormSet):
    ordering_widget = forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'})
    deletion_widget = forms.HiddenInput

    def save(self, commit=True):
        instances = super().save(commit=True)

        for form in self.forms:
            if not (self.can_delete and self._should_delete_form(form)):
                form.instance.order = form.cleaned_data['ORDER']
                form.instance.save()

        return instances

    def clean(self):
        super().clean()
        if all(map(lambda f: f.cleaned_data.get('DELETE', False), self.forms)):
            raise ValidationError("Schema must contain at least one column")


ColumnFormSet = forms.inlineformset_factory(
    Schema, Column,
    formset=BaseColumnInlineFormSet,
    fields=('name', 'data_type', 'minimal', 'maximal'),
    labels={
        'name': 'Column name',
        'data_type': 'Type',
        'minimal': 'From',
        'maximal': 'To',
    },
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        'data_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        'minimal': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
        'maximal': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
    },
    extra=0,
    can_order=True,
    can_delete=True,
)

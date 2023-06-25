from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase


class TestAddAttrsTag(SimpleTestCase):
    class TestForm(forms.Form):
        test_field = forms.CharField(widget=forms.TextInput())

    def _render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_class_attrs_set(self):
        rendered = self._render_template(
            '{% load additional_tags %}'
            '{% for field in form %}'
            '{{ field|add_attrs:"form-control" }}'
            '{%endfor%}',
            context={'form': self.TestForm()}
        )

        self.assertIn("class=\"form-control\"", rendered)

    def test_multiple_attrs_set(self):
        rendered = self._render_template(
            '{% load additional_tags %}'
            '{% for field in form %}'
            '{{ field|add_attrs:"class:form-control,id:field-1" }}'
            '{%endfor%}',
            context={'form': self.TestForm()}
        )

        self.assertIn("class=\"form-control\"", rendered)
        self.assertIn("id=\"field-1\"", rendered)

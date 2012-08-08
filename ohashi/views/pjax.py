import os.path

from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView


class PJAXResponseMixin(TemplateResponseMixin):
    def get_context_data(self, **kwargs):
        context = super(PJAXResponseMixin, self).get_context_data(**kwargs)
        context['pjax_template'] = self._pjaxify_template_name(self.template_name)
        return context

    def get_template_names(self):
        names = super(PJAXResponseMixin, self).get_template_names()
        if self.request.META.get('HTTP_X_PJAX', False):
            names = [self._pjaxify_template_name(names)]
            self.pjax_template_name = names
        return names

    def _pjaxify_template_name(self, name):
        return '%s.pjax%s' % os.path.splitext(self.template_name)


class PJAXDetailView(PJAXResponseMixin, BaseDetailView):
    pass


class PJAXListView(PJAXResponseMixin, BaseListView):
    pass


class PJAXTemplateView(PJAXResponseMixin, View):
    def get_context_data(self, **kwargs):
        return {
            'params': kwargs,
            'pjax_template': self._pjaxify_template_name(self.template_name)
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

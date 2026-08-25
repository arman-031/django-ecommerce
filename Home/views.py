from django.shortcuts import render
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'Home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.request.session.get('my_name','arman')
        return context

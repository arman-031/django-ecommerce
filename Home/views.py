from django.views.generic import TemplateView
from product.models import Product, Category


class HomeView(TemplateView):
    template_name = 'Home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.all()

        for category in categories:
            category.category_image = Product.objects.filter(
                category=category
            ).first()

        context['categories'] = categories
        context['products'] = Product.objects.all()

        return context
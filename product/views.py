from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView

from product.models import Product, Category, Color, Size


class ProductDetailView(DetailView):
    template_name = 'product/detail.html'
    model = Product


class ProductListView(TemplateView):
    template_name = 'product/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all()

        # Search
        query = self.request.GET.get('q')

        if query:
            products = products.filter(
                title__icontains=query
            )

        # Color filter
        color = self.request.GET.get('color')

        if color:
            products = products.filter(
                color__id=color
            )

        # Size filter
        size = self.request.GET.get('size')

        if size:
            products = products.filter(
                size__id=size
            )



        # Pagination
        paginator = Paginator(products, 6)

        page_number = self.request.GET.get('page')

        page_obj = paginator.get_page(page_number)

        context['products'] = page_obj
        context['page_obj'] = page_obj

        context['colors'] = Color.objects.all()
        context['sizes'] = Size.objects.all()

        context['query'] = query
        context['selected_color'] = color
        context['selected_size'] = size

        return context


class CategoryProductView(TemplateView):
    template_name = 'product/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = get_object_or_404(
            Category,
            slug=kwargs['slug']
        )

        products = Product.objects.filter(
            category=category
        )

        # Search
        query = self.request.GET.get('q')

        if query:
            products = products.filter(
                title__icontains=query
            )

        # Color filter
        color = self.request.GET.get('color')

        if color:
            products = products.filter(
                color__id=color
            )

        # Size filter
        size = self.request.GET.get('size')

        if size:
            products = products.filter(
                size__id=size
            )

        # Pagination
        paginator = Paginator(products, 6)

        page_number = self.request.GET.get('page')

        page_obj = paginator.get_page(page_number)

        context['products'] = page_obj
        context['page_obj'] = page_obj

        context['colors'] = Color.objects.all()
        context['sizes'] = Size.objects.all()

        context['category'] = category
        context['query'] = query
        context['selected_color'] = color
        context['selected_size'] = size

        return context


class NavbarPartialView(TemplateView):
    template_name = 'includes/navbar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        return context
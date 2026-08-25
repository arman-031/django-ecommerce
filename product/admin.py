from django.contrib import admin
from .import models
from product.models import Product, Color, Size, Information


class InformationAdmin(admin.StackedInline):
    model = models.Information

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price')
    inlines = [InformationAdmin,]
admin.site.register(Color)
admin.site.register(Size)






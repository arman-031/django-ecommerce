from django.db import models

from account.models import User
from product.models import Product


class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    total_price = models.IntegerField(default=0)
    created=models.DateTimeField(auto_now_add=True)
    is_paid=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'سبد خرید'

    def __str__(self):
        return self.user.phone


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='items')
    size=models.CharField(max_length=10)
    color=models.CharField(max_length=10)
    quantity=models.SmallIntegerField()
    price=models.PositiveIntegerField()
    class Meta:
        verbose_name_plural = 'سبد محصولات'

class Discount(models.Model):
    name=models.CharField(max_length=10,unique=True)
    discount=models.SmallIntegerField(default=0)
    quantity=models.SmallIntegerField(default=1)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'تخفیف'




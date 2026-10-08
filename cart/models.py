from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from account.models import User
from product.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    checkout_token = models.UUIDField(null=True, blank=True, unique=True, editable=False)
    applied_discount = models.ForeignKey(
        'Discount', on_delete=models.SET_NULL, null=True, blank=True,
    )
    discount_applied = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name_plural = 'سفارش‌ها'
        constraints = [
            models.CheckConstraint(condition=models.Q(total_price__gte=0), name='order_total_nonnegative'),
        ]

    def __str__(self):
        return self.user.phone


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='items')
    size = models.CharField(max_length=120, blank=True)
    color = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total(self):
        return self.price * self.quantity

    class Meta:
        verbose_name_plural = 'اقلام سفارش'
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1, quantity__lte=99), name='order_item_quantity_range'),
            models.CheckConstraint(condition=models.Q(price__gte=0), name='order_item_price_nonnegative'),
        ]


class Discount(models.Model):
    name = models.CharField(max_length=10, unique=True)
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'تخفیف‌ها'
        constraints = [
            models.CheckConstraint(condition=models.Q(discount__gte=0, discount__lte=100), name='discount_percentage_range'),
        ]

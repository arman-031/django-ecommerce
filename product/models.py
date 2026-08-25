from django.db import models

class Size(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title

class Color(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=120)
    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    discount = models.FloatField()
    image = models.ImageField(upload_to='products')
    size = models.ManyToManyField(Size,blank=True,null=True,related_name='products')
    color = models.ManyToManyField(Color,related_name='products')
    category = models.ManyToManyField(Category,related_name='products',blank=True,null=True)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'محصولات'

    def __str__(self):
        return self.title

class Information(models.Model):
    product = models.ForeignKey(Product,null=True,on_delete=models.CASCADE,related_name='Information')
    text = models.TextField()

    def __str__(self):
        return self.text[:30]
from django.db import models

class Size(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'سایز'

class Color(models.Model):
    title = models.CharField(max_length=120)
    class Meta:
        verbose_name_plural = 'رنگ '

    def __str__(self):
        return self.title

class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,related_name='sub')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'دسته بندی'

class Product(models.Model):
    category = models.ManyToManyField(Category)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    discount = models.FloatField()
    image = models.ImageField(upload_to='products')
    size = models.ManyToManyField(Size,blank=True,related_name='products')
    color = models.ManyToManyField(Color,related_name='products')
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
    class Meta:
        verbose_name_plural = 'توضیحات'
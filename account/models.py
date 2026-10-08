from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, phone,  password=None):
        """
        Creates and saves a User with the given phone, date of
        birth and password.
        """
        if not phone:
            raise ValueError("Users must have an phone address")

        user = self.model(
            phone=phone,

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone,  password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            phone,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="آدرس ایمیل",
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    fullname = models.CharField(max_length=50,verbose_name='نام کامل')
    phone = models.CharField(max_length=12,unique=True,verbose_name="شماره همراه")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name_plural = 'کاربران'


    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_active and self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_active and self.is_admin

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Otp(models.Model):
    phone=models.CharField(max_length=11)
    code=models.SmallIntegerField()
    expires_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.phone


class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses')
    fullname=models.CharField(max_length=50)
    email=models.EmailField(blank=True,null=True)
    phone=models.CharField(max_length=12)
    address=models.CharField(max_length=300)
    postcode=models.CharField(max_length=30)

    def __str__(self):
        return self.user.phone
    class Meta:
        verbose_name_plural = 'آدرس'
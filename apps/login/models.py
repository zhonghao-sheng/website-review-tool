from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(models.Model):
    username = models.CharField('Username', max_length=50)
    password = models.CharField('Password', max_length=16)

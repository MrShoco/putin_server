from django.db import models
from django.contrib.auth.models import User


class File(models.Model):
    file = models.FileField(upload_to="track/")


class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars')
    user = models.OneToOneField(User)
    total_distance = models.FloatField(default=0)



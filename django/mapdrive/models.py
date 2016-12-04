from django.db import models
from django.contrib.auth.models import User


class File(models.Model):
    file = models.FileField(upload_to="track/")
    processed = models.BooleanField(default=False)

class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars')
    user = models.OneToOneField(User)
    total_distance = models.FloatField(default=0)

class ProcessResultArtifact(models.Model):
    file = models.ForeignKey(File)
    url = models.CharField(max_length=255, default='')
    seconds = models.CharField(max_length=255, default='')

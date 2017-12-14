from django.db import models


class UserInfo(models.Model):
    username = models.CharField(max_length=32)


class UserType(models.Model):
    title = models.CharField(max_length=32)

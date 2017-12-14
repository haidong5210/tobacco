from django.db import models


class UserInfo(models.Model):
    username = models.CharField(max_length=32)

    def __str__(self):
        return self.username


class UserType(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title
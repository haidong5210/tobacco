from django.db import models


class UserInfo(models.Model):
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=64,verbose_name="密码")
    email = models.EmailField(verbose_name="邮箱")
    type = models.ForeignKey(verbose_name="类型",to="UserType")
    host = models.ManyToManyField(verbose_name="主机",to="Host")
    gender_tuple = (
        (1,"男"),
        (2,"女")
    )
    gender = models.IntegerField(verbose_name="性别",choices=gender_tuple)

    def __str__(self):
        return self.username


class UserType(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Host(models.Model):
    hostname = models.CharField(verbose_name='主机名',max_length=32)
    ip = models.GenericIPAddressField(verbose_name="IP",protocol='ipv4')
    port = models.IntegerField(verbose_name='端口')

    def __str__(self):
        return self.hostname
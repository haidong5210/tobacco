from webmaster.server import sites
from app01 import models
from django.conf.urls import url
from django.shortcuts import HttpResponse
from django.forms import ModelForm


class MyMasterModel(sites.MasterModel):
    list_display = ["id","username","password","email"]
    condition_list = ["username__contains","email__contains"]
    show_search_input = True
sites.site.register(models.UserInfo, MyMasterModel)
sites.site.register(models.UserType)


class HostModel(sites.MasterModel):
    list_display = ["ip","hostname","port"]

    def extr_urls(self):
        url_list=[
            url(r'^xxxx/', self.func)
        ]
        return url_list

    def func(self):
        return HttpResponse("!!1111111")

    class Host(ModelForm):
        class Meta:
            model = models.Host
            fields = "__all__"
            error_messages = {
                "hostname":{
                    "required":'不能为空！！'
                }
            }
    model_form_class = Host
sites.site.register(models.Host,HostModel)
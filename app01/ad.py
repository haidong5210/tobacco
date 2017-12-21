from webmaster.server import sites
from app01 import models
from django.conf.urls import url
from django.shortcuts import HttpResponse
from django.forms import ModelForm


class MyMasterModel(sites.MasterModel):
    def host(self,obj=None,is_head=False):
        if is_head:
            return "主机"
        show_list = []
        for item in obj.host.all():
            show_list.append(item.hostname)
        return ",".join(show_list)

    def gender(self,obj=None,is_head=False):
        if is_head:
            return "性别"
        return obj.get_gender_display()
    list_display = ["id","username","password","email","type",gender,host]
    condition_list = ["username__contains","email__contains"]
    show_search_input = True

    def del_catch(self,request):
        pk_list = request.POST.getlist("pk")
        models.UserInfo.objects.filter(id__in=pk_list).delete()
    del_catch.text="批量删除"
    # catch_list = [del_catch,]
    # show_catch = True
    comb_list = [
                 sites.PacComb("gender",is_choice=True),
                 sites.PacComb("type",multi=True),
                 sites.PacComb("host"),
                 ]
sites.site.register(models.UserInfo, MyMasterModel)


class MyUserTypeModel(sites.MasterModel):
    list_display = ["id", "title"]
sites.site.register(models.UserType,MyUserTypeModel)


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
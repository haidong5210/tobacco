from webmaster.server import sites
from app01 import models
from django.utils.safestring import mark_safe


class MyMasterModel(sites.MasterModel):
    def edit(self,obj=None,is_head=False):
        if is_head:
            return "操作"
        url = str(obj.id)+"/edit"
        return mark_safe("<a href='%s'>编辑</a>"%url)

    def check(self,obj=None,is_head=False):
        if is_head:
            return "#"
        return mark_safe('<input type="checkbox" name="%s">'%obj.id)
    list_display = [check,"id","username",edit]
sites.site.register(models.UserInfo, MyMasterModel)
sites.site.register(models.UserType)
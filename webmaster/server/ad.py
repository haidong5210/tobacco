from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render


class MasterModel(object):
    list_display = []

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site

    @property
    def urls(self):
        return self.get_url()

    def get_url(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name)
        urlpatterns =[
            url(r'^$',self.list_view,name="%s_%s_list"%app_model_name),
            url(r'^add/$',self.add_view,name="%s_%s_add"%app_model_name),
            url(r'^(\d+)/edit/$',self.edit_view,name="%s_%s_edit"%app_model_name),
            url(r'^(\d+)/delete/$',self.delete_view,name="%s_%s_delete"%app_model_name),
        ]
        return urlpatterns

    def list_view(self,request,*args,**kwargs):
        model_set = self.model_class.objects.all()
        return render(request,"list.html",{"model_set":model_set})

    def add_view(self,request,*args,**kwargs):
        return HttpResponse("增加列表")

    def edit_view(self,request,nid,*args,**kwargs):
        return HttpResponse("修改列表")

    def delete_view(self,request,nid,*args,**kwargs):
        return HttpResponse("删除列表")


class MasterSite(object):
    def __init__(self):
        self._registry = {}

    def register(self,model_class,master_class=None):
        if not master_class:
            master_class = MasterModel
        self._registry[model_class] = master_class(model_class,self)

    @property
    def urls(self):
        return self.get_url(),None,"tobacco"

    def get_url(self):
        urlpatterns =[]
        for model_class,master_class in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name
            url_patterns = url(r'^%s/%s/'%(app_name,model_name),include(master_class.urls))
            urlpatterns.append(url_patterns)
        return urlpatterns
site = MasterSite()
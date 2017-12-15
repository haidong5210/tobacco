from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm


class MasterModel(object):
    list_display = []
    show_add_btn = True

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site

    def get_list_display(self):
        """
        处理生成check，删除，编辑按钮
        :return:
        """
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(MasterModel.edit)
            data.append(MasterModel.delete)
            data.insert(0, MasterModel.check)
        return data

    def edit(self,obj=None,is_head=False):
        if is_head:
            return "操作"
        return mark_safe("<a href='%s'>编辑</a>"%self.get_edit_url(obj.id))

    def delete(self,obj=None,is_head=False):
        if is_head:
            return "操作"
        return mark_safe("<a href='%s'>删除</a>"%self.get_delete_url(obj.id))

    def check(self,obj=None,is_head=False):
        if is_head:
            return "#"
        return mark_safe('<input type="checkbox" name="%s">'%obj.id)

    def get_edit_url(self,nid):
        """
        反向生成修改的url
        :param nid:
        :return:
        """
        name = "tobacco:%s_%s_edit" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        current_url = reverse(name, args=(nid,))
        return current_url

    def get_list_url(self):
        """
        反向生成列表的url
        :return:
        """
        name = "tobacco:%s_%s_list" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        current_url = reverse(name)
        return current_url

    def get_add_url(self):
        """
        反向生成添加的url
        :return:
        """
        name = "tobacco:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        current_url = reverse(name)
        return current_url

    def get_delete_url(self,nid):
        """
        反向生成删除的url
        :param nid:
        :return:
        """
        name = "tobacco:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        current_url = reverse(name,args=(nid,))
        return current_url

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
        urlpatterns.extend(self.extr_urls())
        return urlpatterns

    def extr_urls(self):
        """
        自定义添加的url
        :return:[url(.......),url(.......),]
        """
        return []

    def get_add_btn(self):
        return self.show_add_btn

    def list_view(self,request,*args,**kwargs):
        model_set = self.model_class.objects.all()

        def head_list():
            """
            处理表头
            :return:[]
            """
            if self.get_list_display():
                for filed_name in self.get_list_display():
                    if isinstance(filed_name,str):
                        verbose_name = self.model_class._meta.get_field(filed_name).verbose_name
                    else:
                        verbose_name = filed_name(self,is_head=True)
                    yield verbose_name

        def data_list():
            """
            数据处理
            :return:[]
            """
            for obj in model_set:
                field_list = []
                if self.get_list_display():
                    for filed_name in self.get_list_display():
                        if isinstance(filed_name,str):
                            if hasattr(obj,filed_name):
                                field_list.append(getattr(obj,filed_name))
                        else:
                            field_list.append(filed_name(self,obj))
                else:
                    field_list.append(obj)
                yield field_list
        return render(request,"list.html",{"model_set":data_list(),"head_list":head_list(),
                                           "add_url":self.get_add_url(),"is_add":self.get_add_btn()})

    def add_view(self,request,*args,**kwargs):
        class List(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"
        if request.method == "GET":
            form = List()
            return render(request,"add.html",{"form":form})
        else:
            form = List(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            else:
                return render(request, "add.html", {"form": form})

    def edit_view(self,request,nid,*args,**kwargs):
        return HttpResponse("修改列表")

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method == "GET":
            return render(request,"delete.html")
        else:
            self.model_class.objects.filter(pk=nid).delete()
            return redirect(self.get_list_url())


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
from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from tobacco.page.pager1 import Pagination
from django.http import QueryDict


class PacListView(object):
    def __init__(self,master_obj,model_set):
        self.master_obj = master_obj
        self.get_list_display = master_obj.get_list_display()
        self.model_class = master_obj.model_class
        self.model_set = model_set
        self.request = master_obj.request
        pager_obj = Pagination(self.request.GET.get('page', 1), len(self.model_set), self.request.path_info,
                           self.request.GET, per_page_count=3)
        self.pager_obj = pager_obj

    def head_list(self):
        # 处理表头
        head_list = []
        if self.get_list_display:
            for filed_name in self.get_list_display:
                if isinstance(filed_name, str):
                    verbose_name = self.model_class._meta.get_field(filed_name).verbose_name
                else:
                    verbose_name = filed_name(self, is_head=True)
                head_list.append(verbose_name)
        return head_list

    def data_list(self):
        # 处理数据
        data_list = []
        for obj in self.model_set:
            field_list = []
            if self.get_list_display:
                for filed_name in self.get_list_display:
                    if isinstance(filed_name, str):
                        if hasattr(obj, filed_name):
                            field_list.append(getattr(obj, filed_name))
                    else:
                        field_list.append(filed_name(self.master_obj, obj))
            else:
                field_list.append(obj)
            data_list.append(field_list)
        return data_list[self.pager_obj.start:self.pager_obj.end]

    def add_url(self):
        add_url = "%s?%s" % (self.master_obj.get_add_url(),self.master_obj.parm.urlencode())
        return add_url

    def is_add(self):
        return self.master_obj.get_add_btn()


class MasterModel(object):
    list_display = []
    show_add_btn = True
    model_form_class = None

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site
        self.request = None
        self.parm = None
        self.url_encode_key = "_listfilter"

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
        return mark_safe("<a href='%s?%s'>编辑</a>"%(self.get_edit_url(obj.id),self.parm.urlencode()))

    def delete(self,obj=None,is_head=False):
        if is_head:
            return "操作"
        return mark_safe("<a href='%s?%s'>删除</a>"%(self.get_delete_url(obj.id),self.parm.urlencode()))

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

    def wrap(self, view_func):
        """
        装饰器
        给self.request赋值
        :param view_func:
        :return:
        """
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)
        return inner

    def get_url(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name)
        urlpatterns =[
            url(r'^$',self.wrap(self.list_view),name="%s_%s_list"%app_model_name),
            url(r'^add/$',self.wrap(self.add_view),name="%s_%s_add"%app_model_name),
            url(r'^(\d+)/edit/$',self.wrap(self.edit_view),name="%s_%s_edit"%app_model_name),
            url(r'^(\d+)/delete/$',self.wrap(self.delete_view),name="%s_%s_delete"%app_model_name),
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

    def get_model_form_class(self):
        if not self.model_form_class:
            class List(ModelForm):
                class Meta:
                    model = self.model_class
                    fields = "__all__"
            return List
        else:
            return self.model_form_class

    def list_view(self,request,*args,**kwargs):
        self.parm = QueryDict(mutable=True)
        self.parm[self.url_encode_key] = self.request.GET.urlencode()
        model_set = self.model_class.objects.all()
        list_view_obj = PacListView(self,model_set)
        return render(request,"list.html",{"list_view_obj":list_view_obj})

    def add_view(self,request,*args,**kwargs):
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request,"add.html",{"form":form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                list_url = "%s?%s"%(self.get_list_url(),self.request.GET.get(self.url_encode_key))
                return redirect(list_url)
            else:
                return render(request, "add.html", {"form": form})

    def edit_view(self,request,nid,*args,**kwargs):
        model_form_class = self.get_model_form_class()
        obj = self.model_class.objects.filter(pk=nid).first()
        if request.method == "GET":
            form = model_form_class(instance=obj)
            return render(request,"edit.html",{"form":form})
        else:
            form = model_form_class(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                list_url = "%s?%s" % (self.get_list_url(), self.request.GET.get(self.url_encode_key))
                return redirect(list_url)
            else:
                return render(request, "edit.html", {"form": form})

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method == "GET":
            return render(request,"delete.html")
        else:
            self.model_class.objects.filter(pk=nid).delete()
            list_url = "%s?%s" % (self.get_list_url(), self.request.GET.get(self.url_encode_key))
            return redirect(list_url)


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
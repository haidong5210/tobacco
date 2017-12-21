import copy
import json
from django.conf.urls import url,include
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from tobacco.page.pager1 import Pagination
from django.http import QueryDict
from django.db.models import Q
from django.db.models import ForeignKey,ManyToManyField


class PacComb:
    """
    对comb_list的数据封装的类
    """
    def __init__(self,field_name,multi=False,condition=None,is_choice=False):
        """
        封装comb_list内的数据
        :param field_name: 字段名
        :param multi:  是否多选
        :param condition: 显示多少的条件
        :param is_choice: 是否是choice字段
        """
        self.field_name = field_name
        self.multi = multi
        self.condition = condition
        self.is_choice = is_choice

    def get_queryset(self,_field):
        if not self.condition:
            return _field.rel.to.objects.all()
        else:
            return _field.rel.to.objects.filter(**self.condition)

    def get_choice(self,_field):
        return _field.choices


class FilterRow:
    """
    返回到前端的样式，可迭代对象
    """
    def __init__(self,paccomb_obj, data, request):
        """
        :param paccomb_obj: comb——list里存的PacComb的对象
        :param data:  对应字段的所有信息
        :param request:为了得到request.GET
        """
        self.comb_obj = paccomb_obj
        self.data = data
        self.request = request

    def __iter__(self):
        current_id = self.request.GET.get(self.comb_obj.field_name)
        path = self.request.path
        param = copy.deepcopy(self.request.GET)
        param._mutable = True
        #生成全部的url
        if self.comb_obj.field_name in param:
            val = param.pop(self.comb_obj.field_name)      #pop拿出来的值是列表
            yield mark_safe('<a href="%s?%s">全部</a>'%(path,param.urlencode()))
            param.setlist(self.comb_obj.field_name, val)
        else:
            yield mark_safe('<a class="active" href="%s?%s">全部</a>' % (path, param.urlencode()))
        #生成选项的url
        for item in self.data:
            if self.comb_obj.is_choice:
                pk, text = str(item[0]), item[1]
            else:
                pk, text = str(item.pk), str(item)
            if not self.comb_obj.multi:    #单选
                param[self.comb_obj.field_name] = pk
                if current_id == pk:
                    yield mark_safe('<a class="active" href="%s?%s">%s</a>'%(path,param.urlencode(),text))
                else:
                    yield mark_safe('<a href="%s?%s">%s</a>' % (path, param.urlencode(), text))
            else:    #多选
                _params = copy.deepcopy(param)
                id_list = _params.getlist(self.comb_obj.field_name)
                if pk in id_list:
                    id_list.remove(pk)
                    _params.setlist(self.comb_obj.field_name,id_list)
                    yield mark_safe('<a class="active" href="%s?%s">%s</a>' % (path, _params.urlencode(), text))
                else:
                    id_list.append(pk)
                    _params.setlist(self.comb_obj.field_name, id_list)
                    yield mark_safe('<a href="%s?%s">%s</a>' % (path, _params.urlencode(), text))


class PacListView(object):
    """
    封装list_view
    """
    def __init__(self,master_obj,model_set):
        self.master_obj = master_obj                         # 下面的MasterModel的对象
        self.model_set = model_set                           # 对象的表所有数据

        self.get_list_display = master_obj.get_list_display()
        self.model_class = master_obj.model_class
        self.request = master_obj.request
        pager_obj = Pagination(self.request.GET.get('page', 1), len(self.model_set), self.request.path_info,
                           self.request.GET, per_page_count=3)
        self.pager_obj = pager_obj                                     #分页组件的对象
        self.show_search_input = master_obj.get_show_search_input()     #是否展示搜索框
        self.condition_value = master_obj.request.GET.get("condition", "")  # 在url上直接写搜索条件，显示在input框上用到
        self.get_catch_list = master_obj.get_catch_list()             #得到批量操作的列表
        self.show_catch = master_obj.get_show_catch()                 #是否展示批量操作框
        self.comb_list = master_obj.get_comb_list()                   #组合搜索

    def get_catch(self):
        """
        处理批量操作的显示在前端的内容，函数名和函数的自定义text
        :return:
        """
        result = []
        for func in self.get_catch_list:
            temp = {"name":func.__name__,"text":func.text}
            result.append(temp)
        return result

    def head_list(self):
        # 处理表头
        head_list = []
        if self.get_list_display:
            for filed_name in self.get_list_display:
                if isinstance(filed_name, str):
                    verbose_name = self.model_class._meta.get_field(filed_name).verbose_name
                else:
                    verbose_name = filed_name(self.master_obj, is_head=True)
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

    def combinatorial(self):
        """
        通过数据库操作返回每个表中的数据
        :return:
        """
        for paccomb_obj in self.comb_list:
            _field = self.model_class._meta.get_field(paccomb_obj.field_name)
            if isinstance(_field,ForeignKey):
                row = FilterRow(paccomb_obj,paccomb_obj.get_queryset(_field),self.request)
            elif isinstance(_field,ManyToManyField):
                row = FilterRow(paccomb_obj,paccomb_obj.get_queryset(_field),self.request)
            else:
                row = FilterRow(paccomb_obj,paccomb_obj.get_choice(_field),self.request)
            yield row


class MasterModel(object):
    list_display = []      #显示那几个列，字段
    condition_list = []    #搜索对应的字段
    catch_list = []        #批量执行那个操作
    comb_list = []          #组合搜索
    show_add_btn = True
    model_form_class = None
    show_search_input = False
    show_catch = False

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
        return mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.id)

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

    def get_condition_list(self):
        result = []
        if self.condition_list:
            result.extend(self.condition_list)
        return result

    def get_condition(self):
        """
        得到搜索的字段条件，利用Q
        :return:con
        """
        condition = self.request.GET.get("condition")
        con = Q()
        con.connector = "or"
        if condition and self.get_show_search_input():
            for condition_field in self.get_condition_list():
                con.children.append((condition_field,condition))
        return con

    def get_show_search_input(self):
        """
        自定义是否显示搜索框，默认不显示
        :return:
        """
        if self.show_search_input:
            return self.show_search_input

    def get_catch_list(self):
        result = []
        if self.catch_list:
            result.extend(self.catch_list)
        return result

    def get_show_catch(self):
        if self.show_catch:
            return self.show_catch

    def get_comb_list(self):
        result = []
        if self.comb_list:
            result.extend(self.comb_list)
        return result

    def list_view(self,request,*args,**kwargs):
        """
        展示页面
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.parm = QueryDict(mutable=True)
        self.parm[self.url_encode_key] = self.request.GET.urlencode()
        if request.method == "POST" and self.get_show_catch():
            func_str = request.POST.get("list_action")
            catch_func = getattr(self,func_str)
            ret = catch_func(request)
            if ret:
                return ret
        #处理搜索
        comb_condition = {}
        option_list = self.get_comb_list()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                comb_condition["%s__in" % key] = value_list
        model_set = self.model_class.objects.filter(self.get_condition()).filter(**comb_condition).distinct()
        list_view_obj = PacListView(self,model_set)                       #封装的那个对象，只传对象到前端
        return render(request,"list.html",{"list_view_obj":list_view_obj})

    def add_view(self,request,*args,**kwargs):
        model_form_class = self.get_model_form_class()
        _popbackid = request.GET.get('_popbackid')
        if request.method == "GET":
            form = model_form_class()
            return render(request,"add.html",{"form":form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                add_obj = form.save()
                if _popbackid:
                    json_result = {"id":add_obj.pk,"text":str(add_obj),"popbackid":_popbackid}
                    return render(request,"PopResponse.html",{"json_result":json.dumps(json_result)})
                else:
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
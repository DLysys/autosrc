from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import Http404
from utils.visit_info import change_info
from django.core.paginator import Paginator
from apps.users.models import Profile
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.conf import settings
import markdown2


class companyListView(ListView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'companies/index.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'company_list'

    # 页面类型，分类目录或标签列表等
    page_type = ''
    paginate_by = settings.PAGINATE_BY
    page_kwarg = 'companies'
    link_type = 'l'

    # def get_view_cache_key(self):
    #     return self.request.get['pages']
    #
    # @property
    # def page_number(self):
    #     page_kwarg = self.page_kwarg
    #     page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
    #     return page
    #
    # def get_context_data(self, **kwargs):
    #     kwargs['linktype'] = self.link_type
    #     return super(companyListView, self).get_context_data(**kwargs)


# class IndexView(ListView):
#     template_name = 'share_layout/base.html'
#     context_object_name = 'company_list'
#
#     def get_queryset(self):
#         return Company.objects.order_by('-pub_date')[:5]

    # link_type = 'i'
    #
    # def get_queryset_data(self):
    #     company_list = company.objects.filter(type='a', status='p')
    #     return company_list
    #
    # def get_queryset_cache_key(self):
    #     cache_key = 'index_{companies}'.format(companies=self.page_number)
    #     return cache_key


def index(request):
    # change_info(request)  # 更新访问数
    #
    # companys_all = company.objects.order_by('-id')
    # types = company.type_choice
    # paginator = Paginator(companys_all, 15)
    # companies = request.GET.get('companies')
    # companies = paginator.get_page(companies)

    return render(request, 'companies/index.html', locals())


class companyDetailView(DetailView):
    """ 主题详细页 """
    model = Company
    template_name = "companies/company_detail.html"
    context_object_name = "company"
    pk_url_kwarg = 'company_id'

    def get_object(self, queryset=None):
        obj = super(companyDetailView, self).get_object()
        obj.viewed()
        self.object = obj
        # obj.content = markdown2.markdown(obj.content, extras=['fenced-code-blocks'], )
        return obj


# @csrf_exempt
# def company_detail(request, company_id):
#     try:
#         company = company.objects.get(id=company_id)
#         res = companyUser.objects.get(company_id=company_id, user_id=request.user)
#         comments = companyUser.objects.filter(company_id=company_id).exclude(comment=None)
#     except Exception as e:
#         print(e)
#     return render(request, 'companies/company_detail.html', locals())


@csrf_exempt
def author_detail(request, author_id):
    try:
        author = Author.objects.get(id=author_id)
        # res = models.companyUser.objects.get(company_id=author_id, user_id=request.user)
    except Exception as e:
        print(e)
    return render(request, 'companies/author_detail.html', locals())


def company_category(request, category_id):
    """
    其实是书籍分类，为了兼容HTML模板，返回companys
    """
    companys = Book.objects.filter(category_id=category_id)

    return render(request, 'companies/index.html', locals())


def company_type(request, type):
    companys_all = company.objects.filter(type=type)
    types = company.type_choice
    paginator = Paginator(companys_all, 15)
    page = request.GET.get('companies')
    companys = paginator.get_page(page)

    return render(request, 'companies/index.html', locals())


@csrf_exempt
def company_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        company_id = request.POST.get('company_id')
        # try:
        #     company = models.company.objects.get(id=company_id)
        #     if k.author == request.user:
        #         return HttpResponse('{"status":"error"}', content_type='application/json')
        #     else:
        #         pass
        # except Exception as e:
        #     print(e)
        try:
            user_profile = Profile.objects.get(user=request.user)
        except Exception as e:
            user_profile = None
            print(e)
        try:
            companyUser.objects.update_or_create(company_id=company_id, user=request.user, defaults={'comment': content})
            user_profile.point = int(user_profile.point) + 1
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')


@csrf_exempt
@login_required
def company_add(request):
    types = company.type_choice
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        type = request.POST.get('type')

        try:
            company.objects.create(title=title, content=content, author_id=request.user.id,
                                        b_category_id=category, type=type)
            user_profile.point = int(user_profile.point) + 5
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'companies/add.html', locals())


@csrf_exempt
@login_required
def company_support(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        action = request.POST.get('action')
        try:
            company = company.objects.get(id=company_id)
            author_id = company.author_id
        except Exception as e:
            print(e)
            company = None
            author_id = None
        if request.user.id != author_id:
            if action == 'support':
                try:
                    company.support = int(company.support) + 1
                    company.save()
                    companyUser.objects.update_or_create(company_id=company_id, user_id=request.user.id, defaults={'support': 1})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
            else:
                try:
                    company.support = int(company.support) - 1
                    company.save()
                    companyUser.objects.update_or_create(company_id=company_id, user_id=request.user.id, defaults={'support': 0})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"error"}', content_type='application/json')
    else:
        return render(request, 'companies/company_detail.html', locals())


@csrf_exempt
@login_required
def company_collect(request):
    # types = models.company.type_choice
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        action = request.POST.get('action')
        if action == 'collect':
            try:
                companyUser.objects.update_or_create(company_id=company_id, user_id=request.user.id, defaults={'collect': True})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            try:
                companyUser.objects.update_or_create(company_id=company_id, user_id=request.user.id, defaults={'collect': False})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'companies/company_detail.html', locals())


@csrf_exempt
@login_required
def company_edit(request, company_id):
    types = company.type_choice
    try:
        k = company.objects.get(id=company_id)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        type = request.POST.get('type')

        try:
            k.title = title
            k.content = content
            k.b_category_id = category
            k.type = type
            k.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'companies/edit.html', locals())


@csrf_exempt
def company_search(request):
    q = request.GET.get('q')
    companys = company.objects.filter(title__icontains=q)
    paginator = Paginator(companys, 15)
    page = request.GET.get('companies')
    pks = paginator.get_page(page)

    return render(request, 'companies/index.html', locals())


@csrf_exempt
def about(request):

    return render(request, 'companies/about.html', locals())


@csrf_exempt
def google_search(request):

    return render(request, 'companies/google7c5c39bd4748d567.html', locals())


@csrf_exempt
def baidu_search(request):

    return render(request, 'companies/baidu_verify_Z85YzIi6cp.html', locals())


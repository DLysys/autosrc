from django.shortcuts import render
from django.http import HttpResponse
from . import models
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import Http404
from utils.visit_info import change_info
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator


@csrf_exempt
def index(request):
    change_info(request)  # 更新访问数

    ks = models.Knack.objects.order_by('-id')
    types = models.Knack.type_choice
    paginator = Paginator(ks, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'knack/index.html', locals())


@csrf_exempt
def knack_detail(request, knack_id):
    try:
        k = models.Knack.objects.get(id=knack_id)
        # sn = k.knackuser_set.filter(support=1)
        res = models.KnackUser.objects.get(knack_id=knack_id, user_id=request.user)
    except Exception as e:
        print(e)
    return render(request, 'knack/detail.html', locals())


def knack_category(request, category_id):
    ks = models.Knack.objects.filter(k_category_id=category_id)

    return render(request, 'knack/index.html', locals())


def knack_type(request, type):
    ks = models.Knack.objects.filter(type=type)
    types = models.Knack.type_choice
    paginator = Paginator(ks, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'knack/index.html', locals())


@csrf_exempt
def knack_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        knack_id = request.POST.get('knack_id')
        try:
            k = models.Knack.objects.get(id=knack_id)
            if k.author == request.user:
                return HttpResponse('{"status":"error"}', content_type='application/json')
            else:
                pass
        except Exception as e:
            print(e)
        try:
            user_profile = models.Profile.objects.get(user=request.user)
        except Exception as e:
            print(e)
        try:
            models.KnackUser.objects.create(comment=content, knack_id=knack_id, user=request.user)
            user_profile.point = int(user_profile.point) + 1
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


@csrf_exempt
@login_required
def knack_add(request):
    types = models.Knack.type_choice
    try:
        user_profile = models.Profile.objects.get(user=request.user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        type = request.POST.get('type')

        try:
            models.Knack.objects.create(title=title, content=content, author_id=request.user.id,
                                        k_category_id=category, type=type)
            user_profile.point = int(user_profile.point) + 5
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'knack/add.html', locals())


@csrf_exempt
@login_required
def knack_edit(request, knack_id):
    types = models.Knack.type_choice
    try:
        k = models.Knack.objects.get(id=knack_id)
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
            k.k_category_id = category
            k.type = type
            k.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'knack/edit.html', locals())


@csrf_exempt
def knack_search(request):
    q = request.GET.get('q')
    ks = models.Knack.objects.filter(title__icontains=q)
    paginator = Paginator(ks, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'knack/index.html', locals())


def category(request, pk):
    """
    :param request:
    :param pk:
    :return:
    相应分类下的窍门检索
    """
    try:
        cate = models.Category.objects.get(pk=pk)
    except models.Category.DoesNotExist:  # 读取分类，如果不存在，则引发错误，并404
        raise Http404

    ks = cate.c.all()  ## 获取分类下的所有文章
    # return render_to_response('blog/index.html', ## 使用首页的文章列表模版，但加入了的一个`is_category`开关
    #     {"posts": posts,
    #     "is_category": True,
    #     "cate_name": cate.name,
    #     "categories": Category.objects.all()},
    # context_instance=RequestContext(request))


@csrf_exempt
def about(request):

    return render(request, 'knack/about.html', locals())


@csrf_exempt
def google_search(request):

    return render(request, 'knack/googlee7d18a466878ce19.html', locals())

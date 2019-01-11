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


@csrf_exempt
def index(request):
    change_info(request)  # 更新访问数

    ks = models.Knack.objects.order_by('-id')
    types = models.Knack.type_choice

    return render(request, 'knack/index.html', locals())


@csrf_exempt
def knack_detail(request, knack_id):
    try:
        k = models.Knack.objects.get(id=knack_id)
    except Exception as e:
        print(e)
    return render(request, 'knack/detail.html', locals())


def knack_category(request, category_id):
    ks = models.Knack.objects.filter(k_category_id=category_id)

    return render(request, 'knack/index.html', locals())


def knack_type(request, type):
    ks = models.Knack.objects.filter(type=type)
    types = models.Knack.type_choice

    return render(request, 'knack/index.html', locals())


@csrf_exempt
def knack_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        knack_id = request.POST.get('knack_id')
        try:
            models.KnackUser.objects.create(comment=content, knack_id=knack_id, user=request.user)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


@csrf_exempt
@login_required
def knack_add(request):
    types = models.Knack.type_choice
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        type = request.POST.get('type')

        try:
            models.Knack.objects.create(title=title, content=content, author_id=request.user.id,
                                        k_category_id=category, type=type)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'knack/add.html', locals())


@csrf_exempt
def knack_search(request):
    q = request.GET.get('q')
    ks = models.Knack.objects.filter(title__icontains=q)

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

    ks = cate.c.all() ## 获取分类下的所有文章
    # return render_to_response('blog/index.html', ## 使用首页的文章列表模版，但加入了的一个`is_category`开关
    #     {"posts": posts,
    #     "is_category": True,
    #     "cate_name": cate.name,
    #     "categories": Category.objects.all()},
    # context_instance=RequestContext(request))


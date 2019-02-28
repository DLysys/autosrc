from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import Http404
from utils.visit_info import change_info
from django.core.paginator import Paginator
from apps.users.models import Profile


@csrf_exempt
def index(request):
    change_info(request)  # 更新访问数

    articles_all = models.Article.objects.order_by('-id')
    types = models.Article.type_choice
    paginator = Paginator(articles_all, 15)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    return render(request, 'article/index.html', locals())


@csrf_exempt
def article_detail(request, article_id):
    try:
        article = models.Article.objects.get(id=article_id)
        res = models.ArticleUser.objects.get(article_id=article_id, user_id=request.user)
        comments = models.ArticleUser.objects.filter(article_id=article_id).exclude(comment=None)
    except Exception as e:
        print(e)
    return render(request, 'article/article_detail.html', locals())


@csrf_exempt
def author_detail(request, author_id):
    try:
        author = models.Author.objects.get(id=author_id)
        # res = models.articleUser.objects.get(article_id=author_id, user_id=request.user)
    except Exception as e:
        print(e)
    return render(request, 'article/author_detail.html', locals())


def boob_category(request, category_id):
    ks = models.article.objects.filter(b_category_id=category_id)

    return render(request, 'article/index.html', locals())


def article_type(request, type):
    ks = models.Article.objects.filter(type=type)
    types = models.Article.type_choice
    paginator = Paginator(ks, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'article/index.html', locals())


@csrf_exempt
def article_comment(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        article_id = request.POST.get('article_id')
        # try:
        #     article = models.article.objects.get(id=article_id)
        #     if k.author == request.user:
        #         return HttpResponse('{"status":"error"}', content_type='application/json')
        #     else:
        #         pass
        # except Exception as e:
        #     print(e)
        try:
            user_profile = Profile.objects.get(user=request.user)
        except Exception as e:
            print(e)
        try:
            models.articleUser.objects.update_or_create(article_id=article_id, user=request.user, defaults={'comment': content})
            user_profile.point = int(user_profile.point) + 1
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


@csrf_exempt
@login_required
def article_add(request):
    types = models.article.type_choice
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
            models.article.objects.create(title=title, content=content, author_id=request.user.id,
                                        b_category_id=category, type=type)
            user_profile.point = int(user_profile.point) + 5
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'article/add.html', locals())


@csrf_exempt
@login_required
def article_support(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        action = request.POST.get('action')
        try:
            article = models.article.objects.get(id=article_id)
            author_id = article.author_id
        except Exception as e:
            print(e)
            article = None
            author_id = None
        if request.user.id != author_id:
            if action == 'support':
                try:
                    article.support = int(article.support) + 1
                    article.save()
                    models.articleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'support': 1})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
            else:
                try:
                    article.support = int(article.support) - 1
                    article.save()
                    models.articleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'support': 0})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"error"}', content_type='application/json')
    else:
        return render(request, 'article/article_detail.html', locals())


@csrf_exempt
@login_required
def article_collect(request):
    # types = models.article.type_choice
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        action = request.POST.get('action')
        if action == 'collect':
            try:
                models.articleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'collect': True})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            try:
                models.articleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'collect': False})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'article/article_detail.html', locals())


@csrf_exempt
@login_required
def article_edit(request, article_id):
    types = models.article.type_choice
    try:
        k = models.article.objects.get(id=article_id)
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
        return render(request, 'article/edit.html', locals())


@csrf_exempt
def article_search(request):
    q = request.GET.get('q')
    articles = models.article.objects.filter(title__icontains=q)
    paginator = Paginator(articles, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'article/index.html', locals())


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

    return render(request, 'article/about.html', locals())


@csrf_exempt
def google_search(request):

    return render(request, 'article/google7c5c39bd4748d567.html', locals())


@csrf_exempt
def baidu_search(request):

    return render(request, 'article/baidu_verify_Z85YzIi6cp.html', locals())


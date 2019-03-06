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


class IndexView(ListView):
    model = Article
    template_name = 'articles/index.html'
    paginate_by = settings.PAGINATE_BY
    context_object_name = 'articles'

    # def get_queryset(self):
    #     articles = Article.objects.filter(status='p')
    #     return articles


# @csrf_exempt
# def index(request):
#     change_info(request)  # 更新访问数
#
#     articles_all = Article.objects.order_by('-id')
#     types = Article.type_choice
#     paginator = Paginator(articles_all, 15)
#     page = request.GET.get('page')
#     articles = paginator.get_page(page)
#
#     return render(request, 'articles/index.html', locals())


class ArticleDetailView(DetailView):
    """ 主题详细页 """
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"
    pk_url_kwarg = 'article_id'

    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object()
        obj.viewed()
        self.object = obj
        # obj.content = markdown2.markdown(obj.content, extras=['fenced-code-blocks'], )
        return obj


# @csrf_exempt
# def article_detail(request, article_id):
#     try:
#         article = Article.objects.get(id=article_id)
#         res = ArticleUser.objects.get(article_id=article_id, user_id=request.user)
#         comments = ArticleUser.objects.filter(article_id=article_id).exclude(comment=None)
#     except Exception as e:
#         print(e)
#     return render(request, 'articles/article_detail.html', locals())


@csrf_exempt
def author_detail(request, author_id):
    try:
        author = Author.objects.get(id=author_id)
        # res = models.articleUser.objects.get(article_id=author_id, user_id=request.user)
    except Exception as e:
        print(e)
    return render(request, 'articles/author_detail.html', locals())


def article_category(request, category_id):
    """
    其实是书籍分类，为了兼容HTML模板，返回articles
    """
    articles = Book.objects.filter(category_id=category_id)

    return render(request, 'articles/index.html', locals())


def article_type(request, type):
    articles_all = Article.objects.filter(type=type)
    types = Article.type_choice
    paginator = Paginator(articles_all, 15)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    return render(request, 'articles/index.html', locals())


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
            user_profile = None
            print(e)
        try:
            ArticleUser.objects.update_or_create(article_id=article_id, user=request.user, defaults={'comment': content})
            user_profile.point = int(user_profile.point) + 1
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')


@csrf_exempt
@login_required
def article_add(request):
    types = Article.type_choice
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
            Article.objects.create(title=title, content=content, author_id=request.user.id,
                                        b_category_id=category, type=type)
            user_profile.point = int(user_profile.point) + 5
            user_profile.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'articles/add.html', locals())


@csrf_exempt
@login_required
def article_support(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        action = request.POST.get('action')
        try:
            article = Article.objects.get(id=article_id)
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
                    ArticleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'support': 1})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
            else:
                try:
                    article.support = int(article.support) - 1
                    article.save()
                    ArticleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'support': 0})
                    return HttpResponse('{"status":"success"}', content_type='application/json')
                except Exception as e:
                    print(e)
                    return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"error"}', content_type='application/json')
    else:
        return render(request, 'articles/article_detail.html', locals())


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
                ArticleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'collect': True})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
        else:
            try:
                ArticleUser.objects.update_or_create(article_id=article_id, user_id=request.user.id, defaults={'collect': False})
                return HttpResponse('{"status":"success"}', content_type='application/json')
            except Exception as e:
                print(e)
                return HttpResponse('{"status":"fail"}', content_type='application/json')
    else:
        return render(request, 'articles/article_detail.html', locals())


@csrf_exempt
@login_required
def article_edit(request, article_id):
    types = Article.type_choice
    try:
        k = Article.objects.get(id=article_id)
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
        return render(request, 'articles/edit.html', locals())


@csrf_exempt
def article_search(request):
    q = request.GET.get('q')
    articles = Article.objects.filter(title__icontains=q)
    paginator = Paginator(articles, 15)
    page = request.GET.get('page')
    pks = paginator.get_page(page)

    return render(request, 'articles/index.html', locals())


@csrf_exempt
def about(request):

    return render(request, 'articles/about.html', locals())


@csrf_exempt
def google_search(request):

    return render(request, 'articles/google7c5c39bd4748d567.html', locals())


@csrf_exempt
def baidu_search(request):

    return render(request, 'articles/baidu_verify_Z85YzIi6cp.html', locals())


from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from users import forms, models
import json
from django.contrib.auth.models import Group, Permission
from django.http import HttpResponse
from django.core import signing
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth.hashers import make_password
from knack.models import Knack
from utils.notice import WeChatPub


@csrf_exempt
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        passwd = request.POST.get('pass')
        repasswd = request.POST.get('repass')
        username = request.POST.get('username')
        errors = []
        res = User.objects.filter(email=email)
        if res:
            errors.append('该邮箱已注册！')
        res = User.objects.filter(username=username)
        if res:
            errors.append('该昵称已被人使用！')
        else:
            if passwd != repasswd:
                errors.append("两次输入的密码不一致!")
            else:
                user = User.objects.create(email=email, username=username, password=make_password(passwd))
                user.save()
                errors = '注册成功！'
                wechat = WeChatPub()
                title = '新用户注册成功通知'
                content = "<div class=\"normal\">新用户注册成功，邮箱名：%s </div>" % email
                wechat.send_msg(title, content)

    return render(request, 'register.html', locals())


@csrf_exempt
def login_site(request):
    def current_user_url(user):
        _url = 'knack:index'
        # perms = User.get_all_permissions(user)
        # if "knack: index" in perms:
        #     _url = "knack: index"
        # else:
        #     _url = 'knack: index'
        next = request.GET.get('next', None)
        return next and next or reverse(_url)

    if request.method == "POST":
        email = request.POST.get('email')
        passwd = request.POST.get('pass')
        try:
            username = User.objects.get(email=email)
        except Exception as e:
            print(e)
            username = ''
            errors = '用户不存在！'
        user = authenticate(username=username, password=passwd)
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(current_user_url(user))
        else:
            errors = u'登陆失败，邮箱或密码错误！'
    else:
        if request.user.is_authenticated:
            url = current_user_url(request.user)
            return HttpResponseRedirect(url)
        else:
            form = forms.SigninForm()

    return render(request, 'login.html', locals())


@login_required
def logout_site(request):
    logout(request)
    return HttpResponseRedirect(reverse("knack:index"))


def global_settings(request):
    return {'ROOT_CONTEXT': settings.ROOT_CONTEXT}


@login_required
@csrf_exempt
def update_user_info(request):
    """
    用户信息修改
    :param request:
    :return:
    """
    user = request.user
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        city = request.POST.get('city')
        desc = request.POST.get('sign')
        try:
            Profile.objects.update_or_create(user_id=user.id, defaults={'city': city, 'description': desc})
            user.email = email
            user.username = username
            user.save
            return HttpResponse('{"status":"success"}', content_type='application/json')
        except Exception as e:
            print(e)
            return HttpResponse('{"status":"fail"}', content_type='application/json')


def user_home(request, user_id):
    """
    用户主页
    """
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        print(e)
    # assets = Asset.objects.filter(asset_manager_id=user_id)
    # tasks = Task.objects.filter(task_user_id=user_id)
    return render(request, 'home.html', locals())


@login_required
def user_center(request):
    """
    用户中心
    """
    user = request.user
    my_knacks = Knack.objects.filter(author=user)

    return render(request, 'center.html', locals())


@login_required
def user_set(request):
    """
    用户配置
    """
    return render(request, 'set.html')


@login_required
@csrf_protect
def userlist(request):
    user = request.user
    error = ''
    if user.is_superuser:
        area = models.Area.objects.filter(parent__isnull=True)
        city = models.Area.objects.filter(parent__isnull=False)
        return render(request, 'userlist.html', locals())
    else:
        error = '权限错误'
    return render(request, 'errors/error.html', locals())


@login_required
@csrf_protect
def user_list_manage(request):
    user = request.user
    if user.is_superuser:
        ulists = User.objects.order_by('-last_login')
    else:
        ulists = User.objects.filter(profile__parent_email=user.email, email=user.email).order_by('-is_superuser', '-date_joined')
    return render(request, "userlist.html", locals())


@login_required
@csrf_protect
def user_request_cancle(request):
    user = request.user
    error = ''
    if user.is_superuser:
        regist_id_list = request.POST.get('regist_id_list')
        regist_id_list = json.loads(regist_id_list)
        action = request.POST.get('action')
        for regist_id in regist_id_list:
            userregist = get_object_or_404(models.UserRequest, id=regist_id)
            userregist.status = '2'
            userregist.is_check = True
            userregist.is_use = True
            userregist.save()
        error = '已禁用'
    else:
        error = '权限错误'
    return JsonResponse({'error': error})


@login_required
@csrf_protect
def user_disactivate(request):
    user = request.user
    error = ''
    if user.is_superuser:
        user_list = request.POST.get('user_list')
        user_list = json.loads(user_list)
        action = request.POST.get('action')
        for user_mail in user_list:
            user_get = get_object_or_404(User, email=user_mail)
            if action == 'stop':
                user_get.is_check = True
                user_get.is_active = False
            elif action == 'start':
                user_get.is_active = True
            user_get.save()
        error = '已禁用'
    else:
        error = '权限错误'
    return JsonResponse({'error': error})


@csrf_exempt
@login_required
def upload_image(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        user = request.user
        try:
            Profile.objects.update_or_create(user=user, defaults={'avatar': avatar})
            data = {'state': 1}
        except Exception as e:
            print(e)
            data = {'state': 0}

        return JsonResponse(data)

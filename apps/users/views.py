from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from apps.users import models
from apps.users import forms
import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from apps.users.models import Profile
from django.contrib.auth.hashers import make_password
from apps.articles.models import Book, ArticleUser
from utils.notice import WeChatPub
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.core.exceptions import ValidationError


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


def captcha_refresh(request):
    # 内置的源码
    if not request.is_ajax():
        raise Http404

    new_key = CaptchaStore.pick()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
        # 'audio_url': captcha_audio_url(new_key) if settings.CAPTCHA_FLITE_PATH else None
    }

    return HttpResponse(json.dumps(to_json_response), content_type='application/json')


@csrf_exempt
def login_site(request):
    def current_user_url(user):
        _url = 'articles:index'
        # perms = User.get_all_permissions(user)
        # if "articles: index" in perms:
        #     _url = "articles: index"
        # else:
        #     _url = 'articles: index'
        next = request.GET.get('next', None)
        return next and next or reverse(_url)

    if request.method == 'POST':
        cs = CaptchaStore.objects.filter(response=request.POST.get('vercode'), hashkey=request.POST.get('haskey'))
        if cs:
            username = request.POST.get('username')
            passwd = request.POST.get('password')
            try:
                username = User.objects.get(username=username)
            except Exception as e:
                print(e)
                username = ''
                return HttpResponse('{"status":"user error"}', content_type='application/json')
            user = authenticate(username=username, password=passwd)
            if user:
                auth.login(request, user)
                return HttpResponse('{"status":"success"}', content_type='application/json')

                # return HttpResponseRedirect(current_user_url(user))
            else:
                return HttpResponse('{"status":"error"}', content_type='application/json')
                # return HttpResponseRedirect(reverse("users:login"), locals())
        else:
            return HttpResponse('{"status":"vercode error"}', content_type='application/json')

            # return HttpResponseRedirect(reverse("users:login"))
    else:
        if request.user.is_authenticated:
            url = current_user_url(request.user)
            return HttpResponseRedirect(url)
        else:
            hashkey = CaptchaStore.generate_key()
            image_url = captcha_image_url(hashkey)

            form = forms.SigninForm()

    return render(request, 'login.html', locals())


@csrf_protect
def find_pass(request):
    error = ''
    if request.method == 'POST':
        if request.method == 'POST':
            form = forms.ResetpsdRequestForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                user = get_object_or_404(User, email=email)
                if user:
                    hash_res = hashlib.md5()
                    hash_res.update(make_password(email).encode('utf-8'))
                    urlarg = hash_res.hexdigest()
                    models.UserResetpsd.objects.get_or_create(
                        email=email,
                        urlarg=urlarg
                    )
                    res = mails.sendresetpsdmail(email, urlarg)
                    if res:
                        error = '申请已发送，请检查邮件通知，请注意检查邮箱'
                    else:
                        error = '重置邮件发送失败，请重试'
                else:
                    error = '请检查信息是否正确'
            else:
                error = '请检查输入'
        else:
            form = forms.ResetpsdRequestForm()
        return render(request, 'RBAC/resetpsdquest.html', {'form': form, 'error': error})
    else:
        return render(request, 'forget.html')
        # resetpsd = get_object_or_404(models.UserResetpsd,)
        # if resetpsd:
        #     email_get = resetpsd.email
        #     if request.method == 'POST':
        #         form = forms.ResetpsdForm(request.POST)
        #         if form.is_valid():
        #             email = form.cleaned_data['email']
        #             password = form.cleaned_data['password']
        #             repassword = form.cleaned_data['repassword']
        #             if checkpsd(password):
        #                 if password == repassword:
        #                     if email_get == email:
        #                         user = get_object_or_404(User, email=email)
        #                         if user:
        #                             user.set_password(password)
        #                             user.save()
        #                             resetpsd.delete()
        #                             return HttpResponseRedirect('/view/')
        #
        #                         else:
        #                             error = '用户信息有误'
        #                     else:
        #                         error = '用户邮箱不匹配'
        #                 else:
        #                     error = '两次密码不一致'
        #             else:
        #                 error = '密码必须6位以上且包含字母、数字'
        #         else:
        #             error = '请检查输入'
        #     else:
        #         form = forms.ResetpsdForm()
        #     return render(request, 'RBAC/resetpsd.html', {'form': form, 'error': error, 'title': '重置'})


@login_required
def logout_site(request):
    logout(request)
    return HttpResponseRedirect(reverse("articles:index"))


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
    用户中心，收藏
    """
    user = request.user
    my_books = ArticleUser.objects.filter(user=user, collect=True)

    return render(request, 'center.html', locals())


@login_required
def user_set(request):
    """
    用户配置
    """
    return render(request, 'set.html')


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


@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'POST':
        nowpass = request.POST.get('nowpass')
        newpass = request.POST.get('newpass')
        repass = request.POST.get('repass')
        user = authenticate(username=request.user, password=nowpass)

        if user is None:
            return HttpResponse('{"status":"password wrong"}', content_type='application/json')
        else:
            if newpass != repass:
                return HttpResponse('{"status":"not match"}', content_type='application/json')
            else:
                if len(newpass) < 8 or len(newpass) > 36:
                    return HttpResponse('{"status":"password length error"}', content_type='application/json')
                else:
                    request.user.set_password(newpass)
                    request.user.save()
                    return HttpResponse('{"status":"success"}', content_type='application/json')

                    # # 重新登录
                    # user = authenticate(username=username, password=pwd)
                    # if user is not None:
                    #     login(request, user)
                    #
                    # # 页面提示
                    # data['goto_url'] = reverse('user_info')
                    # data['goto_time'] = 3000
                    # data['goto_page'] = True
                    # data['message'] = u'修改密码成功，请牢记新密码'
                    # return render_to_response('message.html', data)

    return render(request, 'set.html', locals())


def clean_pwd_2(self):
    pwd_1 = self.cleaned_data.get('pwd_1')
    pwd_2 = self.cleaned_data.get('pwd_2')




# 验证旧密码是否正确
def clean_pwd_old(self):
    username = self.cleaned_data.get('username')
    pwd_old = self.cleaned_data.get('pwd_old')

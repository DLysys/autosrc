from django import forms
from apps.users import models
from django.forms import ModelForm
from django.forms import widgets
from captcha.fields import CaptchaField


class SigninForm(forms.Form):
    username = forms.CharField(label='账号', max_length=75, widget=forms.TextInput(attrs={'class': 'layui-input', 'placeholder': '域账号【例 san.zhang】'}))
    password = forms.CharField(label='密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '密码'}))
    captcha = CaptchaField(label='验证码')


class Account_Reset_Form(forms.Form):
    firstname = forms.CharField(label='姓', max_length=75, widget=forms.TextInput(attrs={'class': 'layui-input', 'placeholder': '姓'}))
    lastname = forms.CharField(label='名', max_length=75, widget=forms.TextInput(attrs={'class': 'layui-input', 'placeholder': '名'}))
    email = forms.CharField(label='邮箱', max_length=75, widget=forms.TextInput(attrs={'class': 'layui-input', 'placeholder': '邮箱'}))
    password = forms.CharField(label='密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '密码'}))
    repassword = forms.CharField(label='重复密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '重复密码'}))


class ChangPasswdForm(forms.Form):
    old_password = forms.CharField(label='原密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '原密码'}))
    new_password = forms.CharField(label='新密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '新密码'}))
    re_new_password = forms.CharField(label='新密码', max_length=25, widget=forms.PasswordInput(attrs={'class': 'layui-input', 'placeholder': '新密码'}))


class UserInfoForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['mobilephone', 'description']
        widgets = {
            # 'user_num': widgets.TextInput(attrs={'class': 'layui-input', 'placeholder': '编号'}),
            # 'account': widgets.TextInput(attrs={'class': 'layui-input', 'placeholder': '用户名'}),
            # 'company': widgets.TextInput(attrs={'class': 'layui-input', 'placeholder': '公司'}),
            'mobilephone': widgets.TextInput(attrs={'class': 'layui-input', 'placeholder': '个人手机', 'lay-verify': 'phone', 'autocomplete': 'off', 'type': 'tel'}),
            'description': widgets.Textarea(attrs={'class': 'layui-textarea', 'placeholder': '员工介绍'}),
        }

from . import models
from django.forms import ModelForm
from django.forms import widgets


class TaskSyncForm(ModelForm):
    class Meta:
        model = models.Task
        fields = ['task_name', 'task_des']
        widgets = {
            'task_name': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '任务名称，一般以系统名称+版本+日期'}),
            # 'scan_id': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '扫描器对应的任务标识,当前只支持nessus'}),
        }


class TaskCreateForm(ModelForm):
    class Meta:
        model = models.Task
        fields = ['task_name', 'task_target', 'task_des']
        widgets = {
            'task_name': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '任务名称，一般以系统名称+版本+日期'}),
            # 'task_scanner':widgets.Select(attrs={'class':'form-control','placeholder':'扫描节点'}),
            # 'scanner_policy': widgets.Select(attrs={'class': 'form-control', 'placeholder': '扫描策略'}),
            'task_target': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '扫描目标,ip/url'}),
        }


class File(ModelForm):
    class Meta:
        model = models.Files
        fields=['name', 'file_type', 'file']
        widgets ={
            'name':widgets.TextInput(attrs={'class':'form-control','placeholder':'文件名称'}),
            'file_type':widgets.Select(attrs={'class':'form-control','placeholder':'文件类型'}),
            'file':widgets.FileInput(),
            }
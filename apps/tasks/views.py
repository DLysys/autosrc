import time
from apps.tasks import models, forms
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from tasks.scanner_tools.certificate_engine import certificate_engine
import json
import hashlib
from django.conf import settings
from django.contrib.auth.models import User

TASK_STATUS = {
    '1': '待执行',
    '2': '执行中',
    '3': '已暂停',
    '4': '已完成',
}


@login_required
def task_list(request, page):
    tasks_all = models.Task.objects.all().order_by('-id')
    paginator = Paginator(tasks_all, 15)

    try:
        tasks = paginator.get_page(page)
    except PageNotAnInteger:
        tasks = paginator.get_page(1)
    except EmptyPage:
        tasks = paginator.get_page(paginator.num_pages)

    for task in tasks:
        subtasks = task.subtask_for_task.all()
        for subtask in subtasks:
            if subtask.error_msg:
                task.is_error = True
                break

    return render(request, 'tasks/task_list.html', locals())


@login_required
@csrf_exempt
def task_search(request):
    task_name = request.GET.get('task_name')
    task_user = request.GET.get('task_user')
    try:
        task_user_id = User.objects.get(username=task_user).id
        tasks_all = models.Task.objects.filter(task_name__icontains=task_name).filter(task_user_id=task_user_id)
    except Exception as e:
        print(e)
        tasks_all = ''
    paginator = Paginator(tasks_all, 15)
    page = request.GET.get('page')
    tasks = paginator.get_page(page)

    return render(request, 'tasks/task_list.html', locals())


@login_required
@csrf_protect
def task_add_edit(request):
    """ 新建扫描任务 """
    if request.method == "GET":
        task_id = request.GET.get('task_id')
        stypes = models.TASK_TYPE
        if task_id:
            task = models.Task.objects.get(id=task_id)
            staskids = models.SubTask.objects.filter(task_id=task.id).values_list('policy_id', flat=True)

        return render(request, 'tasks/task_add_edit.html', locals())

    if request.method == 'POST':
        _id = request.POST.get('task_id')
        scan_type_id = request.POST.get('scan_type_id')
        task_name = request.POST.get('task_name')
        target_address = request.POST.get('target_address')
        target_username = request.POST.get('target_username')
        target_password = request.POST.get('target_password')
        task_des = request.POST.get('task_des')
        policy_ids = request.POST.getlist('policy_id')
        tasks = models.Task.objects
        if _id:
            task = models.Task.objects.get(id=_id)
            task.task_name = task_name
            task.scan_type_id = scan_type_id
            task.target_address = target_address
            task.target_username = target_username
            task.target_password = target_password
            task.task_des = task_des
            task.task_status = 'pending'
            task.save()
            msg = '更新成功！'
        else:
            task = models.Task.objects.create(
                task_name=task_name,
                scan_type_id=scan_type_id,
                target_address=target_address,
                target_username=target_username,
                target_password=target_password,
                task_des=task_des,
                task_status='pending',
            )
            task.task_num = "S{0}{1}".format(time.strftime('%Y%m%d', time.localtime(time.time())), task.id)
            task.save()
            msg = "添加成功！"
        for spid in policy_ids:
            models.SubTask.objects.update_or_create(policy_id=spid, task_id=task.id, defaults={'scan_id': '--', 'subtask_name': ''})
            # models.SubTask.objects.create(policy_id=spid, task_id=tasks.id, scan_id='--', subtask_name='')
        return HttpResponse(json.dumps({'status': 200, 'msg': msg}), content_type="application/json")


@login_required
@csrf_exempt
def change_scan_type(request):
    """
    选择扫描类型
    :param request:
    :return:
    """
    if request.method == 'POST':
        scan_type_id = request.POST.get("scan_type_id")
        has_user_info = models.ScanType.objects.get(id=scan_type_id).has_user_info

        return JsonResponse({'status': 200, 'has_user_info': has_user_info}, safe=False)


@login_required
@csrf_exempt
def task_action(request):
    """执行任务"""
    if request.method == 'POST':
        task_id = request.POST.get("task_id")
        action = request.POST.get("task_action")
        task = models.Task.objects.filter(id=task_id).first()
        if task:
            subtasks = models.SubTask.objects.filter(task_id=task.id)
            for subtask in subtasks:
                scanner = models.Scanner.objects.get(scanner=subtask.scanner_id)
                task.subtask = subtask
                task.scanner = scanner
                # 获取相应扫描器对象
                engine = scanner.scanner_engine
                eval(engine)(request, task, action)
            # 待处理，已完成，已停止的任务可以再次运行，新结果将覆盖之前结果
            task.task_status = action  # 如果上面任务已经完成，这两行代码会使任务变成运行状态，因此写在函数中
            task.save()
            return JsonResponse({'code': 200})
        else:
            return JsonResponse({'code': 300})


@login_required
@csrf_protect
def task_del(request):
    # 删除 tasks
    if request.method == "POST":
        task_id = request.POST.get('task_id')
        task = models.Task.objects.get(pk=task_id)
        rst = task.delete()
        if rst:
            rst_code = 200
        else:
            rst_code = 300
        return HttpResponse(json.dumps({'status': rst_code}), content_type="application/json")


@login_required
def task_detail(request):
    """ 任务详情 """
    if request.method == "GET":
        user = request.user
        task_id = request.GET.get('task_id')
        task = models.Task.objects.get(id=task_id)
        subtasks = models.SubTask.objects.filter(task_id=task.id)
        if task.scan_result:
            scan_result = eval(task.scan_result)
            summary = scan_result['summary']
            wps = scan_result['wps']
        else:
            scan_result = ''
        # staskids = subtasks.values_list('policy_id', flat=True)
        # scanner_policy = models.Policy.objects.filter(id__in=staskids)
        # tasks.scanner_policy = "".join([s.policy_name for sp in scanner_policy])

    return render(request, 'tasks/detail.html', locals())


@login_required
def task_report(request):
    """ 任务报告 """
    if request.method == "GET":
        subtask_id = request.GET.get('subtask_id')
        subtask = models.SubTask.objects.get(id=subtask_id)

        return render(request, 'tasks/task_report.html', locals())

    if request.method == "POST":
        user = request.user
        subtask_id = request.POST.get('subtask_id')
        subtask = models.SubTask.objects.get(id=subtask_id)
        import os
        filepath = os.path.join(settings.SCAN_RESULT_PDF_FILE_PATH, subtask.report_name)
        sh_file = open(filepath, 'rb')
        response = HttpResponse(sh_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment;filename='+subtask.report_name
        return response


@login_required
@csrf_protect
def taskrequestaction(request, task_id, action):
    user = request.user
    error = ''

    if user.is_superuser:
        task = get_object_or_404(models.Task, task_id=task_id)
        if action == 'access':
            task.task_status = '1'
            task.request_status = '1'
            task.request_note = '已验证'
            task.action_user = user
        elif action == 'deny':
            task.task_status = '5'
            task.request_status = '2'
            task.action_user = user
        task.save()
        error = '审批完成'
    else:
        error = '权限错误'
    return JsonResponse({'error': error})


@login_required
@csrf_protect
def TaskRequestView(request):
    return render(request, 'tasks/taskrequest.html')


@login_required
@csrf_protect
def taskrequesttablelist(request):
    user = request.user
    resultdict = {}
    page = request.POST.get('page')
    rows = request.POST.get('limit')

    if user.is_superuser:
        task_list = models.Task.objects.filter(task_status=0).order_by('task_starttime')
        total = task_list.count()
        task_list = paging(task_list, rows, page)
        data = []
        for item in task_list:
            dic = {}
            dic['task_id'] = item.task_id
            dic['task_name'] = item.task_name
            dic['scan_type'] = item.scan_type
            dic['task_target'] = item.task_target
            dic['task_starttime'] = item.task_starttime
            dic['task_scanner'] = item.task_scanner.scanner_name
            dic['task_user'] = item.task_user.email
            data.append(dic)
        resultdict['code'] = 0
        resultdict['msg'] = "任务列表"
        resultdict['count'] = total
        resultdict['data'] = data
        return JsonResponse(resultdict)


@login_required
@csrf_protect
def TaskSync(request):
    user = request.user
    error = ''
    if user.is_superuser:
        if request.method == 'POST':
            form = forms.TaskSyncForm(request.POST, request.FILES)
            if form.is_valid():
                task_scanner = form.cleaned_data['task_scanner']
                if task_scanner.scanner_type == 'Nessus':
                    try:
                        num_id = models.Task.objects.latest('id').id
                    except:
                        num_id = 0
                    num_id += 1
                    task_id = str('s') + time.strftime('%Y%m%d', time.localtime(time.time())) + str(num_id)
                    task_name = form.cleaned_data['task_name']
                    task_des = form.cleaned_data['task_des']
                    scan_type = '扫描同步'

                    scan_id = form.cleaned_data['scan_id']

                    models.Task.objects.get_or_create(
                        task_id=task_id,
                        task_name=task_name,
                        scan_type=scan_type,
                        task_scanner=task_scanner,
                        scan_id=scan_id,
                        task_status='1',
                        task_user=user,
                        task_des=task_des
                    )
                    error = '创建成功'
                else:
                    error = '扫描节点不支持导入'
        else:
            form = forms.TaskSyncForm()
        return render(request, '../users/templates/formedit.html', {'form': form, 'post_url': 'tasksync', 'error': error})
    else:
        error = '权限错误'
    return render(request, 'errors/error.html', {'error': error})


@login_required
@csrf_protect
def tasktablelist(request):
    user = request.user
    resultdict = {}
    page = request.POST.get('page')
    rows = request.POST.get('limit')

    name = request.POST.get('name')
    if not name:
        name = ''

    key = request.POST.get('key')
    if not key:
        key = ''

    tasktype = request.POST.get('type')
    if not tasktype:
        tasktype = ['安全扫描', '扫描同步']
    else:
        tasktype = [tasktype]

    taskstatus = request.POST.get('status')
    if not taskstatus:
        if user.is_superuser:
            taskstatus = ['1', '2', '3', '4', '5']
        else:
            taskstatus = ['0', '1', '2', '3', '4', '5']
    else:
        taskstatus = [taskstatus]

    if user.is_superuser:
        task_list = models.Task.objects.filter(
            task_name__icontains=name,
            scan_type__icontains=key,
            scan_type__in=tasktype,
            task_status__in=taskstatus
        ).order_by('task_status', '-task_endtime')
    else:
        task_list = models.Task.objects.filter(
            task_user=user,
            task_name__icontains=name,
            scan_type__icontains=key,
            scan_type__in=tasktype,
            task_status__in=taskstatus
        ).order_by('task_status', '-task_endtime')

    total = task_list.count()
    task_list = paging(task_list, rows, page)
    data = []
    for item in task_list:
        dic = {}
        dic['task_id'] = item.task_id
        dic['task_name'] = item.task_name
        dic['scan_type'] = item.scan_type
        dic['task_target'] = item.task_target
        dic['task_status'] = TASK_STATUS[item.task_status]
        dic['task_starttime'] = item.task_starttime
        dic['task_scanner'] = item.task_scanner.scanner_name
        dic['task_user'] = item.task_user.email
        data.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = "任务列表"
    resultdict['count'] = total
    resultdict['data'] = data
    return JsonResponse(resultdict)


# 该段代码用来分页
def paging(deploy_list, limit, offset):
    paginator = Paginator(deploy_list, limit)

    try:
        deploy_list = paginator.page(offset)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        deploy_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        deploy_list = paginator.page(paginator.num_pages)
    return deploy_list


def strtopsd(string):
    hash_res = hashlib.md5()
    hash_res.update(make_password(string).encode('utf-8'))
    urlarg = hash_res.hexdigest()
    return urlarg

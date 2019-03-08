from .hydra import *
from apps.assets.models import Asset


def hydra_engine(request, task, action):
    """
    在线的所有资产进行弱口令扫描
    :param request:
    :param task:
    :param action:
    :return:
    """
    subtask = task.subtask
    if action == 'running':
        subtask.subtask_status = action
        subtask.save()
        task.task_status = action
        task.save()
        assets = Asset.objects.filter(status='online')
        hydra_start.delay(assets, task, subtask)

    if action == 'stopping':
        subtask.subtask_status = action
        subtask.save()
        task.task_status = action
        task.save()
        hydra_stop()

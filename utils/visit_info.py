from apps.articles.models import VisitNumber, UserIp, DayNumber
from django.utils import timezone


def change_info(request):
    count_nums = VisitNumber.objects.filter(id=1)
    if count_nums:
        count_nums = count_nums[0]
        count_nums.count += 1
    else:
        count_nums = VisitNumber()
        count_nums.count = 1
    count_nums.save()

    # 记录访问ip和每个ip的次数
    if 'HTTP_X_FORWARDED_FOR' in request.META: # 获取ip
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
        client_ip = client_ip.split(",")[0] # 所以这里是真实的ip
    else:
        client_ip = request.META['REMOTE_ADDR'] # 这里获得代理ip #
        # print(client_ip)
    ip_exist = UserIp.objects.filter(ip=str(client_ip))
    if ip_exist:
        uobj = ip_exist[0]
        uobj.count += 1
    else:
        uobj = UserIp()
        uobj.ip = client_ip
        uobj.count = 1
    uobj.save()

    # 增加今日访问次数
    date = timezone.now().date()
    today = DayNumber.objects.filter(day=date)
    if today:
        temp = today[0]
        temp.count += 1
    else:
        temp = DayNumber()
        temp.dayTime = date
        temp.count = 1
    temp.save()

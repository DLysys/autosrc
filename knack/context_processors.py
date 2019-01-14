from .models import VisitNumber, Category, KnackUser, Knack
from users.models import User, Profile
from django.db.models import Avg,Count,Min,Max,Sum


def add_variable_to_context(request):
    vm = VisitNumber.objects.first()
    cates = Category.objects.all()
    types = Knack.type_choice

    hot_knacks = KnackUser.objects.values('knack_id').annotate(num_knacks=Count('knack_id')).order_by('-num_knacks')[:5]
    for hk in hot_knacks:
        try:
            hk['title'] = Knack.objects.get(id=hk['knack_id']).title
        except Exception as e:
            print(e)

    zan_knacks = KnackUser.objects.values('knack_id').annotate(num_knacks=Count('knack_id')).order_by('-num_knacks')[:5]
    for hk in hot_knacks:
        try:
            hk['title'] = Knack.objects.get(id=hk['knack_id']).title
        except Exception as e:
            print(e)

    hot_users = Profile.objects.order_by('-point')[:10]
    for hu in hot_users:
        try:
            hu.username = User.objects.get(id=hu.user_id).username
            # hu['avatar'] = Profile.objects.get(user_id=hu['user_id']).avatar
        except Exception as e:
            print(e)

    # hot_users = KnackUser.objects.values('user_id').annotate(num_comments=Count('user_id')).order_by('-num_comments')[:10]
    # for hu in hot_users:
    #     try:
    #         hu['username'] = User.objects.get(id=hu['user_id']).username
    #         hu['avatar'] = Profile.objects.get(user_id=hu['user_id']).avatar
    #     except Exception as e:
    #         print(e)

    return locals()

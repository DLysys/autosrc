from .models import VisitNumber, Category, KnackUser, Knack
from users.models import User
from django.db.models import Avg,Count,Min,Max,Sum


def add_variable_to_context(request):
    vm = VisitNumber.objects.first()
    cates = Category.objects.all()
    types = Knack.type_choice

    hot_knacks = KnackUser.objects.values('knack_id').annotate(num_knacks=Count('knack_id')).order_by('-num_knacks')[:5]
    for hk in hot_knacks:
        hk['title'] = Knack.objects.get(id=hk['knack_id']).title

    hot_users = KnackUser.objects.values('user_id').annotate(num_comments=Count('user_id')).order_by('-num_comments')[:10]
    for hu in hot_users:
        hu['username'] = User.objects.get(id=hu['user_id']).username

    return locals()

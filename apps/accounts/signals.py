from django.db import models
from datetime import date
from .models import UserActivity

def record_activity(user):
    obj, created = UserActivity.objects.get_or_create(
        user=user,
        date=date.today()
    )
    if not created:
        # Mavjud qatorni count + 1 qilamiz
        UserActivity.objects.filter(pk=obj.pk).update(
            count=models.F('count') + 1
        )
    else:
        # Yangi qator — count ni 1 ga qo'yamiz
        obj.count = 1
        obj.save()
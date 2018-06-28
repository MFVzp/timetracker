from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


def get_image_path(instance, filename):
    return '{}/{}/{}'.format(settings.IMAGE_STORAGE_FOLDER, instance.work_diary.user.username, filename)


class WorkDiary(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='work_diaries')
    

class ScreenShot(models.Model):
    work_diary = models.ForeignKey(WorkDiary, on_delete=models.CASCADE, related_name='screenshots', null=True)
    
    image = models.ImageField(upload_to=get_image_path)
    description = models.TextField()
    create_date = models.DateTimeField()

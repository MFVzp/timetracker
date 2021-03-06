# Generated by Django 2.0.6 on 2018-06-28 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import work_diary.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScreenShot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=work_diary.models.get_image_path)),
                ('description', models.TextField()),
                ('create_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='WorkDiary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_diaries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='screenshot',
            name='work_diary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screenshots', to='work_diary.WorkDiary'),
        ),
    ]

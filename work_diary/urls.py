from django.urls import path

from work_diary.views import (
    WorkDiaryView,
    UploadScreenshotsView
)


urlpatterns = [
    path('index/', WorkDiaryView.as_view(), name='work_diary'),
    path('upload_screenshots/', UploadScreenshotsView.as_view(), name='upload_screenshots'),
]

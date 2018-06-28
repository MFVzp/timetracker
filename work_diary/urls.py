from django.urls import path

from work_diary.views import (
    WorkDiaryView,
    UploadScreenshotsView,
    UploadScreenshotsAPIView
)


urlpatterns = [
    path('index/', WorkDiaryView.as_view(), name='work_diary'),
    path('upload_screenshots/', UploadScreenshotsView.as_view(), name='upload_screenshots'),
    path('api/upload_screenshots/', UploadScreenshotsAPIView.as_view()),
]

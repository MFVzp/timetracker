import datetime

from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


from work_diary.models import (
    WorkDiary,
    ScreenShot
)
from work_diary.serializers import ScreenShotsSerializer


class WorkDiaryView(TemplateView):
    template_name = 'work_diary.html'
    
    def get_context_data(self, **kwargs):
        context = super(WorkDiaryView, self).get_context_data(**kwargs)

        context['screenshots'] = dict()
        queryset = ScreenShot.objects.filter(
            work_diary__user=self.request.user,
            create_date__year=datetime.datetime.now().year,
            create_date__month=datetime.datetime.now().month,
            create_date__day=datetime.datetime.now().day,
        ).order_by('create_date')
        for shot in queryset:
            if shot.create_date.hour not in context['screenshots']:
                context['screenshots'][shot.create_date.hour] = {i: None for i in range(6)}
            context['screenshots'][shot.create_date.hour][int(shot.create_date.minute / 10)] = shot
        return context
    

class UploadScreenshotsView(TemplateView):
    template_name = 'upload_screenshots.html'

    def post(self, request, *args, **kwargs):
        user = get_user_model().objects.all()[0]
        work_diary = WorkDiary.objects.get(user=user)
        ss = ScreenShot.objects.create(
            work_diary=work_diary,
            image=request.FILES.get('image'),
            description=request.POST.get('description'),
            create_date=datetime.datetime.now()
        )
        print(ss)
        
        return redirect('upload_screenshots')


class UploadScreenshotsAPIView(GenericAPIView):
    serializer_class = ScreenShotsSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.all()[0]
            work_diary = WorkDiary.objects.get(user=user)
            data = serializer.validated_data
            data['work_diary'] = work_diary
            print(data)
            serializer.create(data)
            return Response({'status': 'success'})
        else:
            return Response({
                'status': 'fail',
                'errors': serializer.errors
            })

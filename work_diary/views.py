import datetime

from django.views.generic import TemplateView
from django.shortcuts import redirect

from work_diary.models import (
    WorkDiary,
    ScreenShot
)


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
        work_diary = WorkDiary.objects.get(user=request.user)
        ss = ScreenShot.objects.create(
            work_diary=work_diary,
            image=request.FILES.get('image'),
            description=request.POST.get('description'),
            create_date=datetime.datetime.now()
        )
        print(ss)
        
        return redirect('upload_screenshots')

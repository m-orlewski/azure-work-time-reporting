from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Sum
from work_time_reporting.models import WorkTime

def home(request):
    return render(request, 'work_time_reporting/index.html')

@csrf_exempt
def add_work_time(request):
    try:
        date = request.POST['date']
        hours = request.POST['hours']
    except(KeyError):
        return render(request, 'work_time_reporting/index.html', {
            'message': "You must include: date, hours worked",
        })
    else:
        work_time = WorkTime()
        work_time.date = date
        work_time.hours = hours
        WorkTime.save(work_time)
        return render(request, 'work_time_reporting/index.html', {
            'message': f"Entry added: ({date}: {hours})"
        })

def generate_summary(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        entries = WorkTime.objects.filter(date__range=[start_date, end_date]).order_by("date")
        date_range = f'{start_date} - {end_date}'
    elif start_date:
        entries = WorkTime.objects.filter(date__gte=start_date).order_by("date")
        date_range = f'after {start_date}'
    elif end_date:
        entries = WorkTime.objects.filter(date__lte=end_date).order_by("date")
        date_range = f'before {end_date}'
    else:
        entries = WorkTime.objects.all().order_by("date")
        date_range = 'None'

    total_hours = entries.aggregate(sum=Sum('hours'))['sum']

    context = {
        'entries': entries,
        'date_range': date_range,
        'total_hours': total_hours
    }

    return render(request, 'work_time_reporting/index.html', context)
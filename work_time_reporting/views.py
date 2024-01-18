from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout

from django.db.models import Sum
from work_time_reporting.models import WorkTime

import logging

logger = logging.getLogger(__name__)

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

def home(request):
    logger.info('INFO - rendering home page')
    return render(request, 'work_time_reporting/index.html')

@csrf_exempt
def login_view(request):
    logger.info('INFO - rendering login page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is None:
            logger.info('INFO - login failed')
            return render(request, 'work_time_reporting/login.html', {'message': 'Invalid username or password'})

        logger.info('INFO - login successful')
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'work_time_reporting/login.html')
    
@csrf_exempt
def logout_view(request):
    logger.info('INFO - rendering logout page')
    logout(request)
    return redirect('home')



@csrf_exempt
@user_passes_test(is_superuser, login_url='/login')
def add_work_time(request):
    logger.info('INFO - rendering add_work_time page')
    try:
        date = request.POST['date']
        hours = request.POST['hours']
    except(KeyError):
        logger.error('ERROR - add_work_time endpoint: date/hours worked not found')
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

@user_passes_test(is_superuser, login_url='/login')
def generate_summary(request):
    logger.info('INFO - rendering generate_summary page')
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
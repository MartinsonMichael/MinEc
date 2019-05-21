from django.shortcuts import render
from dbcontroller.models import Company
import dbcontroller.dbziploader as dbc

def index(request, **kwargs):
    cnt = Company.objects.all().count()
    func = kwargs['func']
    if func is not None:
        if func == 'test':
            dbc.test()



    return render(request, 'control.html', {
        'cnt': cnt,
        'func': func
    })

from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from dbcontroller.models import Company
import dbcontroller.dbziploader as dbc


def index(request, **kwargs):
    print('request on control')
    cnt = Company.objects.all().count()
    func = kwargs['func']
    if func is not None:
        if func == 'test':
            dbc.test()
        if func == 'fill':
            dbc.fill()
        if func == 'test_with_load':
            dbc.test_with_load()

        return HttpResponseRedirect('/api/control/')

    return render(request, 'control.html', {
        'cnt': cnt,
        'func': "None",
    })

from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from dbcontroller.models import Company
import dbcontroller.dbziploader as dbc


def index(request, **kwargs):
    print('request on control')
    cnt = -1
    try:
        cnt = Company.objects.all().count()
    finally:
        pass
    func = kwargs['func']
    if func is not None:
        if func == 'test':
            dbc.test()
        if func == 'fill':
            dbc.fill()
        if func == 'test_with_load':
            dbc.test_with_load()
        if func == 'penis':
            dbc.foo()

        return HttpResponseRedirect('/api/control/')

    return render(request, 'control.html', {
        'cnt': cnt,
        'func': "None",
    })

from django.shortcuts import render
# from django.http import HttpResponse
# import datetime
from . import forms
from dbcontroller import models
from dbcontroller import filters
from django_tables2 import RequestConfig
from django.views.generic import TemplateView


def index(request):
    return render(request, 'rest_template.html')

    # table, form = get_table_form(request)
    #
    # par_dict = {
    #     'form': form,
    #     'filter': table,
    # }
    #
    # # return render(
    # #     request, 'block_try.html', par_dict
    # # )
    # return render(request, 'simple_request.html', par_dict)


def get_table_form(request):
    if request.method == 'POST':
        return process_post(request)
    if 'has_table' in request.session:
        form = request.session['form']
        table = process_table(request)
        return table, form

    table = None
    form = forms.BaseRequestForm()
    return table, form


def process_post(request):
    form = forms.BaseRequestForm(request.POST)
    table = process_table(request)

    request.session['has_table'] = True
    # request.session['table'] = table
    request.session['form'] = request.POST

    return table, form


def process_table(request):
    table = filters.CompanyFilter(request.GET, queryset=models.Company.objects.all())
    # RequestConfig(request).configure(table)
    return table

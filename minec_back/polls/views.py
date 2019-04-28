from django.shortcuts import render
from django.http import HttpResponse
from dbcontroller import dbziploader


def index(request):
    dbziploader.test()
    # try:
    #
    # except:
    #     print('\n***\nexception in test\n**\n')
    #     pass

    return HttpResponse("Download complite!")

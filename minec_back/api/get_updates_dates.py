from django.http import HttpResponse
from dbcontroller.models import LoadDates
import json
import datetime


def get_as_table(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = '*'

    def my_ser(x):
        if isinstance(x, (datetime.datetime, datetime.date)):
            return str(x.day) + '.' + str(x.month) + '.' + str(x.year)

    #query = LoadDates.objects.all().order_by('-date').values('date')

    #header = list(query[0].keys())
    table_header = json.dumps(['date'])
    #table_header = json.dumps(header)
    table_human_header = json.dumps(['Дата обновления'])
    #table_body = json.dumps(list(query), default=my_ser)
    table_body = json.dumps([{'date': '18.06.2019'}])

    response.content = json.dumps({
        'table_header': table_header,
        'table_human_header': table_human_header,
        'table_body': table_body,
        'table_error': json.dumps([]),
    })

    return response
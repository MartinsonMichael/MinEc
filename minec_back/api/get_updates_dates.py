from django.http import HttpResponse


def get_last():
    pass

def get_as_table():
    resp = HttpResponse()
    resp[]


    resp.content = json.dumps({
        'table_header': table_header,
        'table_human_header': table_human_header,
        'table_body': table_body,
        'table_error': json.dumps(table_err),
    })
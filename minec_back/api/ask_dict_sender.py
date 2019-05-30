from django.http import HttpResponse
import json
from dbcontroller.model_support import create_ASK_DICT

ASK_DICT = None


def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):
    global ASK_DICT
    if ASK_DICT is None:
        ASK_DICT = create_ASK_DICT()
    resp = get_template_HTTP_RESPONSE()
    resp.content = json.dumps({
        'ask_dict': ASK_DICT,
    })
    return resp
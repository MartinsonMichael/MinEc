from django.shortcuts import render, HttpResponse, HttpResponseRedirect
import dbcontroller.schedule_master as master


def get_last():
    if master.ScheduleTable.objects.count() == 0:
        return [{}]
    last_date = master.ScheduleTable.objects.order_by('-date').values()[0]['date']
    print(last_date)
    status = []
    for base in master.PAGE_TYPES.keys():
        base_name = base.__name__
        url_name = master.PAGE_TYPES[base]['url_name']
        cur =  dict()
        cur['name'] = base_name
        q = master.ScheduleTable.objects.filter(date=last_date)
        for _type in ['load', 'unzip']:
            if q.filter(type=_type).filter(zip_file_name=url_name).count() == 0:
                cur[_type] = '0/1'
            else:
                cur[_type] = '1/1'

        if q.filter(zip_file_name=url_name).filter(type='unzip').count() != 0:
            cur['add'] = str(q.filter(type='add').filter(base_name=base_name).count()) +\
                         '/' +\
                         str(q.filter(type='need_to_add').filter(zip_file_name=url_name)[0].file_name)
        else:
            cur['add'] = '0/None'

        status.append(cur)

    status = [[(x, y) for x, y in item.items()] for item in status]

    return status


def index(request, **kwargs):
    status = get_last()
    print(status)
    return render(request, 'control2.html', context={'status': status})

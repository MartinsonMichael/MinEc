# Generated by Django 2.1.7 on 2019-05-28 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0027_auto_20190528_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='region_name',
            field=models.TextField(choices=[(1, 'адыгея республика'), (2, 'башкортостан республика'), (3, 'бурятия республика'), (4, 'алтай республика'), (5, 'дагестан республика'), (6, 'ингушетия республика'), (7, 'кабардино-балкарская республика'), (8, 'калмыкия республика'), (9, 'карачаево-черкесская республика'), (10, 'карелия республика'), (11, 'коми республика'), (12, 'марий эл республика'), (13, 'мордовия республика'), (14, 'саха /якутия/ республика'), (15, 'северная осетия - алания республика'), (16, 'татарстан республика'), (17, 'тыва республика'), (18, 'удмуртская республика'), (19, 'хакасия республика'), (20, 'чеченская республика'), (21, 'чувашская республика - чувашия'), (22, 'алтайский край'), (23, 'краснодарский край'), (24, 'красноярский край'), (25, 'приморский край'), (26, 'ставропольский край'), (27, 'хабаровский край'), (28, 'амурская область'), (29, 'архангельская область'), (30, 'астраханская область'), (31, 'белгородская область'), (32, 'брянская область'), (33, 'владимирская область'), (34, 'волгоградская область'), (35, 'вологодская область'), (36, 'воронежская область'), (37, 'ивановская область'), (38, 'иркутская область'), (39, 'калининградская область'), (40, 'калужская область'), (41, 'камчатский край'), (42, 'кемеровская область'), (43, 'кировская область'), (44, 'костромская область'), (45, 'курганская область'), (46, 'курская область'), (47, 'ленинградская область'), (48, 'липецкая область'), (49, 'магаданская область'), (50, 'московская область'), (51, 'мурманская область'), (52, 'нижегородская область'), (53, 'новгородская область'), (54, 'новосибирская область'), (55, 'омская область'), (56, 'оренбургскаяобласть область'), (57, 'орловская область'), (58, 'пензенская область'), (59, 'пермский край'), (60, 'псковская область'), (61, 'ростовская область'), (62, 'рязанская область'), (63, 'самарская область'), (64, 'саратовская область'), (65, 'сахалинская область'), (66, 'свердловская область'), (67, 'смоленская область'), (68, 'тамбовская область'), (69, 'тверская область'), (70, 'томская область'), (71, 'тульская область'), (72, 'тюменская область'), (73, 'ульяновская область'), (74, 'челябинская область'), (75, 'забайкальский край'), (76, 'ярославская область'), (77, 'москва город'), (78, 'санкт-петербург город'), (79, 'еврейская автономная область'), (83, 'ненецкий автономный округ'), (86, 'ханты-мансийский автономный округ - югра автономный округ'), (87, 'чукотский автономный округ'), (89, 'ямало-ненецкий автономный округ'), (91, 'крым республика'), (92, 'севастополь город')], default='НЕИЗВЕСТНО', verbose_name='Название региона'),
        ),
    ]

# Generated by Django 2.1.7 on 2019-05-21 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0024_auto_20190521_1806'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Income',
            new_name='BaseIncome',
        ),
    ]
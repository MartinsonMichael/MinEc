# Generated by Django 2.1.7 on 2019-06-10 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alive',
            name='_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dbcontroller.Company'),
        ),
    ]

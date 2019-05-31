# Generated by Django 2.1.7 on 2019-05-21 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0019_auto_20190516_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(verbose_name='дата создания компании')),
                ('date_disappear', models.DateField(null=True, verbose_name='дата прекращения существования')),
                ('still_alive', models.BooleanField(default=True, verbose_name='еще существует?')),
                ('still_not_found', models.BooleanField(null=True, verbose_name='technical filed')),
            ],
        ),
        migrations.RemoveField(
            model_name='company',
            name='still_alive',
        ),
        migrations.AddField(
            model_name='alive',
            name='inn',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dbcontroller.Company'),
        ),
    ]
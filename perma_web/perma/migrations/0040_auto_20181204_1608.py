# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-04 16:08
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models
from django.conf import settings


def handle_existing_users(apps, schema_editor):
    """
    All customers who currently have a price should keep it.
    All others should get the default price.
    """
    LinkUser = apps.get_model('perma', 'LinkUser')
    users_without_prices = LinkUser.objects.filter(base_rate=Decimal('0.00'))
    for user in users_without_prices:
        user.base_rate = Decimal(settings.DEFAULT_BASE_RATE)
        user.save()


def handle_existing_registrars(apps, schema_editor):
    """
    All customers who currently have a price should keep it.
    All others should get the default price.
    """
    Registrar = apps.get_model('perma', 'Registrar')
    registrars_without_prices = Registrar.objects.filter(base_rate=Decimal('0.00'))
    for registrar in registrars_without_prices:
        registrar.base_rate = Decimal(settings.DEFAULT_BASE_RATE_REGISTRAR)
        registrar.save()


class Migration(migrations.Migration):

    dependencies = [
        ('perma', '0039_auto_20181121_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicallinkuser',
            name='base_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), help_text='Base rate for calculating subscription cost.', max_digits=19),
        ),
        migrations.AlterField(
            model_name='historicalregistrar',
            name='base_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), help_text='Base rate for calculating subscription cost.', max_digits=19),
        ),
        migrations.AlterField(
            model_name='linkuser',
            name='base_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), help_text='Base rate for calculating subscription cost.', max_digits=19),
        ),
        migrations.AlterField(
            model_name='registrar',
            name='base_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('50.00'), help_text='Base rate for calculating subscription cost.', max_digits=19),
        ),
        migrations.RunPython(handle_existing_users, migrations.RunPython.noop),
        migrations.RunPython(handle_existing_registrars, migrations.RunPython.noop)
    ]

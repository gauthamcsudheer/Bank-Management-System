# Generated by Django 4.2.7 on 2023-12-12 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0011_alter_customer_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]

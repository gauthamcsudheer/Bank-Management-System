# Generated by Django 4.2.7 on 2023-12-12 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0007_alter_account_account_number_alter_account_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(default=0, max_length=15),
        ),
    ]

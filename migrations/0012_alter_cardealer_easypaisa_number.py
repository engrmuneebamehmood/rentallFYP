# Generated by Django 5.0.6 on 2024-06-20 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_alter_order_cnic_back_alter_order_cnic_front'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardealer',
            name='easypaisa_number',
            field=models.CharField(max_length=15),
        ),
    ]

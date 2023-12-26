# Generated by Django 4.2.8 on 2023-12-20 06:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("task", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="clickevent",
            name="city",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="clickevent",
            name="click_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="clickevent",
            name="country",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="clickevent",
            name="region",
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
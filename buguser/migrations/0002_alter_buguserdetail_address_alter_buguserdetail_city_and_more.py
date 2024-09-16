# Generated by Django 5.0.3 on 2024-05-07 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buguser", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buguserdetail",
            name="address",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="city",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="country",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="dob",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="first_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="last_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="buguserdetail",
            name="phone",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
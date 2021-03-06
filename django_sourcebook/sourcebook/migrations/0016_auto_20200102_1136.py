# Generated by Django 3.0.2 on 2020-01-02 16:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0015_auto_20200102_1135"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foiarequestitem",
            name="modifications",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                default=list,
                help_text="list any modifications you've made to your original request",
                size=None,
            ),
        ),
    ]

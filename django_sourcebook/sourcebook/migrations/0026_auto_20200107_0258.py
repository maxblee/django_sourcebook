# Generated by Django 3.0.2 on 2020-01-07 07:58

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0025_auto_20200105_0522"),
    ]

    operations = [
        migrations.AddField(
            model_name="foiarequestbase",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="scheduledfoiacontent",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contacts",
                to="sourcebook.Source",
            ),
        ),
        migrations.AddIndex(
            model_name="scheduledfoiacontent",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="sourcebook__search__15ec9e_gin"
            ),
        ),
    ]

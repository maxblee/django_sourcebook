# Generated by Django 3.0.2 on 2020-01-02 16:51

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0016_auto_20200102_1136"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="foiarequestitem", options={"verbose_name": "FOIA Request Item"},
        ),
        migrations.AlterField(
            model_name="foiarequestitem",
            name="modifications",
            field=django_better_admin_arrayfield.models.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                default=list,
                help_text="list any modifications you've made to your original request",
                size=None,
            ),
        ),
    ]

# Generated by Django 3.0.2 on 2020-01-05 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0024_auto_20200104_0056"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="related_foia_request",
            field=models.ForeignKey(
                blank=True,
                help_text="If this contact is related to a FOIA request (e.g. to nag a FOIA officer), note that contact here",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="sourcebook.FoiaRequestItem",
                verbose_name="Related FOIA Request",
            ),
        ),
        migrations.AlterField(
            model_name="source",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("db", "Database administrator"),
                    ("rp", "Person affected (anecdotal source)"),
                    ("e", "Expert"),
                    ("pr", "Spokesperson, PR-Rep"),
                    ("f", "Public Records Officer"),
                    ("o", "Public/Company Official"),
                    ("i", "Company or business employee (current or former)"),
                ],
                max_length=2,
            ),
        ),
    ]
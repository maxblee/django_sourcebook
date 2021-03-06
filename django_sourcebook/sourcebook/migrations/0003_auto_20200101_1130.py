# Generated by Django 3.0.1 on 2020-01-01 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0002_auto_20200101_0407"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="foiarequest", options={"verbose_name": "FOIA Request"},
        ),
        migrations.AlterModelOptions(
            name="state", options={"ordering": ["fips_code"]},
        ),
        migrations.AlterModelOptions(
            name="story", options={"verbose_name_plural": "stories"},
        ),
        migrations.AlterField(
            model_name="contact",
            name="addl_notes",
            field=models.TextField(blank=True, verbose_name="additional notes"),
        ),
        migrations.AlterField(
            model_name="document",
            name="addl_notes",
            field=models.TextField(blank=True, verbose_name="additional notes"),
        ),
        migrations.AlterField(
            model_name="foiarequest",
            name="expedited_processing",
            field=models.TextField(
                blank=True, verbose_name="justification for expedited processing"
            ),
        ),
        migrations.AlterField(
            model_name="foiarequest",
            name="fee_waiver",
            field=models.TextField(blank=True, verbose_name="Fee waiver justification"),
        ),
        migrations.AlterField(
            model_name="foiarequest",
            name="requested_records",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="project",
            name="long_description",
            field=models.TextField(
                help_text="Provide a more detailed description of the project"
            ),
        ),
        migrations.AlterField(
            model_name="projecttask",
            name="description",
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="source",
            name="notes",
            field=models.TextField(
                blank=True, help_text="Random notes about this person."
            ),
        ),
    ]

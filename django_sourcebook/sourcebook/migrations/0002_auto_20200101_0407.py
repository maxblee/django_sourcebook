# Generated by Django 3.0.1 on 2020-01-01 09:07

from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ("sourcebook", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="state",
            name="foia_template",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="foia_templates/",
                validators=[utils.validators.validate_template_extension],
                verbose_name="Public Records act template",
            ),
        ),
    ]

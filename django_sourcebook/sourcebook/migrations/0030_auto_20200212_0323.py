# Generated by Django 3.0.2 on 2020-02-12 08:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sourcebook', '0029_auto_20200210_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foiarequestitem',
            name='recipient_name',
        ),
        migrations.RemoveField(
            model_name='scheduledfoiaagency',
            name='recipient_name',
        ),
        migrations.AddField(
            model_name='foiarequestitem',
            name='recipient',
            field=models.ForeignKey(blank=True, limit_choices_to={'source_type': 'f'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sourcebook.Source'),
        ),
        migrations.AddField(
            model_name='scheduledfoiaagency',
            name='recipient',
            field=models.ForeignKey(blank=True, limit_choices_to={'source_type': 'f'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sourcebook.Source'),
        ),
    ]

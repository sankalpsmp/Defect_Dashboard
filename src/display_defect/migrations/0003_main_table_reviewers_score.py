# Generated by Django 3.0.7 on 2020-09-19 12:29

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('display_defect', '0002_remove_main_table_reviewers_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='main_table',
            name='reviewers_score',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
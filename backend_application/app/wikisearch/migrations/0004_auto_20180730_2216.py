# Generated by Django 2.0.7 on 2018-07-30 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wikisearch', '0003_auto_20180730_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='text',
            field=models.TextField(
                help_text='initial text of article in wikipedia',
                verbose_name='inittext'),
        ),
    ]

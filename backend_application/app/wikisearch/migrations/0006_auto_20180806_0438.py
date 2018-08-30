# Generated by Django 2.0.7 on 2018-08-06 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wikisearch', '0005_article_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='page_rank',
            field=models.FloatField(default=0, help_text='rank of the page', verbose_name='page_rank'),
        ),
    ]

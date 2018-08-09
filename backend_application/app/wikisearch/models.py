from django.db import models

# Create your models here.


class Article(models.Model):

    title = models.CharField('title', max_length=200, help_text='title of article')
    url = models.CharField('URL', max_length=1000, help_text='url of wiki article')
    links = models.TextField('dependings links',  help_text='url of wiki article', default='None')
    text = models.TextField('inittext', help_text='initial text of article in wikipedia')
    page_rank = models.FloatField('page_rank', help_text='rank of the page',default=0)


    def __str__(self):
        return f'{self.title} : {self.text}'

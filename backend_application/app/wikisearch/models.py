from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField('title',max_length=200, help_text='title of article')
    url = models.CharField('URL', max_length=200, help_text='url of wiki article')
    text = models.CharField('inittext', max_length=2000, help_text='initial text of article in wikipedia')

    def __str__(self):
        return f'{self.title} : {self.text}'
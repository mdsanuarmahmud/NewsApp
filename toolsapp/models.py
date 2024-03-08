from django.db import models
from userapp.models import *
from tinymce import models as tinymce_models
from ckeditor_uploader.fields import RichTextUploadingField


class generated_news_list(models.Model):
    source_link = models.CharField(max_length=500)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')
    content = RichTextUploadingField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True) 
    website_url = models.CharField(max_length=250, null=True, blank=True)
    username = models.CharField(max_length=250, null=True, blank=True)
    app_pass =  models.CharField(max_length=250, null=True, blank=True)
    post_status = models.CharField(max_length=50, null=True, blank=True)
    category_name = models.CharField(max_length=250, null=True, blank=True)
    feature_img_status = models.CharField(max_length=50, null=True, blank=True)
    generated_time = models.DateTimeField(auto_now=True)
    schedule_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.source_link
    

class news_generate_Command(models.Model):
    title = models.TextField(default="Generate a blog article's title, written in English, for this Ibiza-related article: <<link>>")
    news_body = models.TextField(default="Generate a blog article, written in English, for this Ibiza-related article: <<link>>")
    image_generation = models.TextField(default='Gegenrate a image on this title : <<title>>')
    

    def __str__(self):
        return 'Info tools bulk posting commands'
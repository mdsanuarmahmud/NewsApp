from django.db import models
from userapp.models import *



class OpenAI_API(models.Model):
    api_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=300)
    model_name = models.CharField(max_length=300)
    error_status = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.api_name}, API key : {self.api_key}"

class Website_List(models.Model):
    website_name = models.CharField(max_length=250)
    website_url = models.URLField()
    username = models.CharField(max_length=250, null=True, blank=True)
    application_password = models.CharField(max_length=250)

    def __str__(self):
        return f"Website Name : {self.website_name}"
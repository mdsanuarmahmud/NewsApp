# cron.py
from .models import *
from time import sleep
from random import choice
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import requests
import shutil
import os
import json
import base64
from time import sleep
import re
from openai import OpenAI
from dashapp.models import *
from django.db.models import F
from time import sleep
import logging
logger = logging.getLogger('django')



def news_generating_job():
    pending_news = generated_news_list.objects.filter(status='Pending') 
    for pending_news_model in pending_news:
        command_model = news_generate_Command.objects.first()
        source_link = pending_news_model.source_link
        news_body_command = command_model.news_body.replace('<<link>>',source_link)
        news_title_command = command_model.title.replace('<<link>>',source_link)


        title = text_render('',news_title_command, pending_news_model).replace('"','').title()
        body = news_body(news_body_command, pending_news_model)
        if body != 'OpenAI Error' and title != 'OpenAI Error':
            pending_news_model.content = body
            pending_news_model.title = title
            pending_news_model.status = 'Generated'
        else:
            pending_news_model.status = 'Failed'
        pending_news_model.save()
        print(' source : ',source_link)
        
    
def text_render(previous_prompt, prompt, newsmodel):
    api= OpenAI_API.objects.first()
    try:
        logger.info(api.api_key)
        client = OpenAI(api_key=api.api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": previous_prompt},
                {"role": "user", "content": prompt}
            ],
            model=api.model_name,
        )
        output = response.choices[0].message.content

    except Exception as oops:
        logger.info("Openai error : " + str(oops))
        api.error_status = "Openai error : " + str(oops)
        api.save()
        newsmodel.error = 'Error Message from OpenAI server: ' + str(oops)
        newsmodel.logs = 'OpenAI API Error...'
        newsmodel.save()
        output = 'OpenAI Error'
    return output


def text_format(text):
    logger.info('Text formating .................')
    if text:
        rc1 = choice([3, 4])
        rc2 = choice([10, 11])
        rc3 = choice([16, 17])
        p_format = text.replace('?', '?---').replace('.', '.---').replace('!', '!---').strip().split(sep='---')
        p = '<p>' + ''.join(p_format[:rc1]) + '</p>' + '<p>' + ''.join(p_format[rc1:7]) + '</p>' + '<p>' + ''.join(p_format[7:rc2]) + '</p>' + '<p>' + ''.join(p_format[rc2:13]) + '</p>' + '<p>' + ''.join(p_format[13:rc3]) + '</p>' + '<p>' + ''.join(p_format[rc3:20]) + '</p>' + '<p>' + ''.join(p_format[20:]) + '</p>'
        text = p.replace('  ', ' ').replace('<p></p>', '').replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('<p> ','<p>').replace('\n','').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '').replace('10.', '').replace('<p>  ','<p>').replace('<p> ','<p>').replace('.','. ').replace('.  ','. ').replace('!!','')
        return text
    else:
        return 'Text dose not Generated from OpenAI' 


def news_body(command, model):
    print('Content body .................')
    model.logs = 'Content Body...'
    model.save()  
    news_body_data  = text_format(text_render('',command + "Please don't give me title", model))
    return news_body_data
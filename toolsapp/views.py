from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from dashapp.models import *
from django.db.models import F
from toolsapp.models import *
from .task import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.http import JsonResponse
from django.template.loader import render_to_string
import shutil
import threading
import logging
from datetime import datetime
import random
from time import sleep
from openai import OpenAI
import json
from django.core.serializers.json import DjangoJSONEncoder
logger = logging.getLogger("django")

# Create your views here.



scheduler_thread = None
@login_required(login_url='login')
def news_generating(request):
        website = Website_List.objects.all()
        link_pending = generated_news_list.objects.filter(status='Pending')
        running_link = generated_news_list.objects.filter(status='Running')


        template = 'toolsapp/generating_news.html'
        context = {'link_pending': link_pending,
                'website': website,
                'running_link': running_link
                }
        if request.method == 'POST':
            news_links = request.POST.get('news_links')
            links = news_links.split('\n')
            
            for link in links:
                link = link.strip()
                if link:
                    generated_news_list.objects.create(source_link=link, status='Pending')

            global scheduler_thread
            if scheduler_thread is None or not scheduler_thread.is_alive():
                scheduler_thread = threading.Thread(target=news_generating_job)
                scheduler_thread.start()
            return redirect('news_generating')
        else:
            return render(request, template, context=context)





# Completed posts...
        

@login_required(login_url='login')
def complete_generated_news(request):
    try:
        complete_generated_news= generated_news_list.objects.filter(status='Generated').order_by('title')
        context = {'complete_generated_news':complete_generated_news}
    except:
        context = {'complete_generated_news':''}
    template = 'toolsapp/generated_news.html'
    return render(request, template, context=context)




@login_required(login_url='login')
def complete_generated_single_view(request, id):
    generated_news = generated_news_list.objects.get(pk=id)
    templeate = 'toolsapp/generated_single_view.html'
    if request.method == 'POST':
        title = request.POST.get('title')
        website_id = request.POST.get('website_id')
        website_info = Website_List.objects.values('website_url', 'username', 'application_password').get(pk=website_id)
        website_url = website_info['website_url']
        username = website_info['username']
        app_pass = website_info['application_password']
        category = request.POST.get('category')
        post_status = request.POST.get('post_status')
        img_status = request.POST.get('img_status')
        scheduled_date_str = request.POST.get('scheduled_date')
        post_body = request.POST.get('content')

        logger.info(' Title :  ' + str(title))
        logger.info(' website_id :  ' + str(website_id))
        logger.info(' website_url : ' + str(website_url))
        logger.info(' username : ' + str(username))
        logger.info(' app_pass : '+ str(app_pass))
        logger.info(' category : '+ str(category))
        logger.info(' post_status : ' + str(post_status))
        logger.info("post_body : ", post_body)
        logger.info(str(img_status) + str(img_status))
        logger.info(str(scheduled_date_str))

        json_url = website_url + 'wp-json/wp/v2'
        token = base64.standard_b64encode((username + ':' + app_pass).encode('utf-8'))
        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

        logger.info('title : ' + title)


        category_id = create_category(category, generated_news, json_url, headers)
        image_id = feature_image_dalle(title, generated_news, json_url, headers, img_status)
        if scheduled_date_str:
            formatted_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d')
            formatted_date_str = formatted_date.strftime('%Y-%m-%dT%H:%M:%S')  # Convert datetime to string
            if category_id == 0:
                post = {'title': title, 'slug': title.replace('','-'), 'status': 'future', 'date': formatted_date_str,
                        'content': post_body, 'format': 'standard', 'featured_media': int(image_id)}
            else:
                post = {'title': title, 'slug': title.replace('','-'), 'status': 'future', 'date': formatted_date_str,
                        'content': post_body, 'categories': [category_id], 'format': 'standard', 'featured_media': int(image_id)}
            r = requests.post(json_url + '/posts', headers=headers, data=json.dumps(post, cls=DjangoJSONEncoder))  # Serialize datetime using DjangoJSONEncoder
            if r.status_code == 201:
                generated_news.status = 'Posted'
                generated_news.logs = 'Scheduled'
                generated_news.save()
                logger.info("Scheduled Completed")
            else:
                generated_news.status = 'Failed'
                generated_news.logs = str(r.content)
                generated_news.save()
                logger.info("Scheduled Failed,,, error is :  " + str(r.content))
        else:
            if category_id == 0:
                post = {'title': title, 'slug': title.replace('','-'), 'status': post_status, 'content': post_body, 'format': 'standard',
                        'featured_media': int(image_id)}
            else:
                post = {'title': title, 'slug': title.replace('','-'), 'status': post_status, 'content': post_body,
                        'categories': [category_id], 'format': 'standard',
                        'featured_media': int(image_id)}
            r = requests.post(json_url + '/posts', headers=headers, json=post)  
            if r.status_code == 201:
                generated_news.status = 'Posted'
                generated_news.logs = 'Published or Drafted'
                generated_news.save()
                logger.info("Published or Drafted")
            else:
                generated_news.status = 'Failed'
                generated_news.logs = str(r.content)
                generated_news.save()
                logger.info("Published or Drafted Failed,,, error is :  " + str(r.content))
        return redirect('complete_generated_news')


    else:
        website = Website_List.objects.all()
        logger.info(str(generated_news))
        logger.info(str(generated_news.source_link))
        context = {'generated_news':generated_news, 'website':website}
        return render(request, templeate, context=context)

@login_required(login_url='login') 
def delete_complete_generated_news(request, id):
        api = generated_news_list.objects.get(pk=id)
        api.delete()
        return redirect('complete_generated_news')

@login_required(login_url='login') 
def delete_all_complete_generated_news(request):
        posts = generated_news_list.objects.all().exclude(status__in=["Failed", "Pending", "Running", "Posted"])
        posts.delete()
        return redirect('complete_generated_news')
    





# Posted news -------------------------------
@login_required(login_url='login')
def posted_news(request):
    try:
        complete_generated_news= generated_news_list.objects.filter(status='Posted').order_by('title')
        context = {'complete_generated_news':complete_generated_news}
    except:
        context = {'complete_generated_news':''}
    template = 'toolsapp/posted_news.html'
    return render(request, template, context=context)

@login_required(login_url='login')
def posted_news_single_view(request, id):
    templeate = 'toolsapp/posted_single_view.html'
    generated_news = generated_news_list.objects.get(pk=id)
    logger.info(str(generated_news))
    logger.info(str(generated_news.source_link))
    context = {'generated_news':generated_news}
    return render(request, templeate, context=context)

@login_required(login_url='login') 
def delete_posted_news(request, id):
        api = generated_news_list.objects.get(pk=id)
        api.delete()
        return redirect('posted_news')

@login_required(login_url='login') 
def delete_all_posted_news(request):
        posts = generated_news_list.objects.all().exclude(status__in=["Failed", "Pending", "Running", "Generated"])
        posts.delete()
        return redirect('posted_news')


    
 # Pending or Running Posts....
@login_required(login_url='login')    
def delete_pending_news(request, id):
        post = generated_news_list.objects.get(pk=id)
        post.delete()
        return redirect('news_generating')


@login_required(login_url='login')    
def delete_all_pending_news(request):
        keywords = generated_news_list.objects.all().exclude(status__in=["Generated", "Failed","Posted"])
        keywords.delete()
        return redirect('news_generating')   
    
    
    
# Fails Posts....
@login_required(login_url='login')    
def failed_generated_news(request):
        fail_news = generated_news_list.objects.filter(status='Failed').order_by('title')
        context = {'fail_news':fail_news}
        template = 'toolsapp/failed_news.html'
        return render(request, template, context=context)

@login_required(login_url='login')
def failed_generated_single_view(request, id):
    templeate = 'toolsapp/failed_single_view.html'
    failed_news = generated_news_list.objects.get(pk=id)
    context = {'fail_post':failed_news}
    return render(request, templeate, context=context)

@login_required(login_url='login') 
def delete_failed_generated_news(request, id):
        post = generated_news_list.objects.get(pk=id)
        post.delete()
        return redirect('failed_generated_news')

@login_required(login_url='login') 
def delete_all_failed_generated_news(request):
        posts = generated_news_list.objects.all().exclude(status__in=["Generated", "Pending", "Running"])
        posts.delete()
        return redirect('failed_generated_news')






# Functions ----------------------------------------------------------------

def create_category(cat_name, bulkmodel, json_url, headers):
    bulkmodel.logs = 'Category...'
    bulkmodel.save()  
    logger.info('Category .................') 
    id = 0
    if len(cat_name) > 0:
        data = {"name":cat_name}
        try:
            cat = requests.post(json_url + '/categories', headers=headers, json=data)
            id = str(json.loads(cat.content.decode('utf-8'))['id'])
        except KeyError:
            cat = requests.get(json_url + '/categories', headers=headers)
            cat_id = json.loads(cat.content.decode('utf-8'))
            for cat in cat_id:
                if cat_name.lower() == cat['name'].lower():
                    id = str(cat['id'])
    bulkmodel.logs = 'Category done...'
    bulkmodel.save()  
    logger.info('Category Done.................') 
    return id  



def feature_image_dalle(command, model, json_url, headers, img_status):
    api = OpenAI_API.objects.first()
    if img_status == 'enable':
        logger.info('Feature Img...')
        model.logs = 'Feature Img...'
        model.save()
        
        # Call DALL-E to generate image
        client = OpenAI(api_key=api.api_key)

        response = client.images.generate(
            model="dall-e-3",
            prompt=command,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        try:
            # Extract image URL from the response
            image_url = response.data[0].url
            
            # Download the image content
            image_response = requests.get(image_url)
            image_content = image_response.content
            
            # Specify the file path where you want to save the image
            img_path = os.path.join('newsimage/', "f.jpg")
            
            # Write the image content to the file
            with open(img_path, "wb") as img_file:
                img_file.write(image_content)
            
            # Upload image
            media = {'file': open(img_path, 'rb')}
            image_upload_response = requests.post(json_url + '/media', headers=headers, files=media)
            
            # Check if the image upload was successful
            if image_upload_response.status_code == 200:
                post_id = str(json.loads(image_upload_response.content.decode('utf-8'))['id'])
                logger.info('Feature Img Done..')
                model.logs = 'Feature Img Done...'
                model.save()
                # Remove image file after uploading
                os.remove(img_path)
                return post_id
            else:
                raise Exception("Failed to upload image: " + str(image_upload_response.status_code))
        
        except Exception as e:
            logger.error('Feature Img Failed: ' + str(e))
            model.error = 'Feature Img Failed...'
            model.logs = 'Feature Img Failed...'
            model.save()
            # Remove image file in case of failure
            if os.path.exists(img_path):
                os.remove(img_path)
            return 0
    else:
        return 0





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
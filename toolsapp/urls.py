# URL Mapping in App URL file----------------------
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', views.news_generating, name='news_generating'),

    path('complete-generated-news', views.complete_generated_news, name='complete_generated_news'), 
    path('complete-generated-single-view/<id>', views.complete_generated_single_view, name='complete_generated_single_view'), 
    path('delete-complete-generated-news/<id>', views.delete_complete_generated_news, name='delete_complete_generated_news'),  
    path('delete-all-complete-generated-news', views.delete_all_complete_generated_news, name='delete_all_complete_generated_news'), 


    path('posted-news', views.posted_news, name='posted_news'), 
    path('posted-news-single-view/<id>', views.posted_news_single_view, name='posted_news_single_view'), 
    path('delete-posted-news/<id>', views.delete_posted_news, name='delete_posted_news'),  
    path('delete-all-posted-news', views.delete_all_posted_news, name='delete_all_posted_news'),

    path('delete-pending-news/<id>', views.delete_pending_news, name='delete_pending_news'),  
    path('delete-all-pending-news', views.delete_all_pending_news, name='delete_all_pending_news'),

    path('failed-generated-news', views.failed_generated_news, name='failed_generated_news'), 
    path('failed-generated-single-view/<id>', views.failed_generated_single_view, name='failed_generated_single_view'), 
    path('delete-failed-generated-news/<id>', views.delete_failed_generated_news, name='delete_failed_generated_news'),
    path('delete-all-failed-generated-news', views.delete_all_failed_generated_news, name='delete_all_failed_generated_news')
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
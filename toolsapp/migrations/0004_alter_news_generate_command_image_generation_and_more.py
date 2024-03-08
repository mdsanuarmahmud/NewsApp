# Generated by Django 5.0.2 on 2024-03-03 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolsapp', '0003_remove_generated_news_list_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news_generate_command',
            name='image_generation',
            field=models.TextField(default='Gegenrate a image on this title : <<title>>'),
        ),
        migrations.AlterField(
            model_name='news_generate_command',
            name='news_body',
            field=models.TextField(default='Generate a blog article, written in English, for this Ibiza-related article: <<link>>'),
        ),
        migrations.AlterField(
            model_name='news_generate_command',
            name='title',
            field=models.TextField(default="Generate a blog article's title, written in English, for this Ibiza-related article: <<link>>"),
        ),
    ]
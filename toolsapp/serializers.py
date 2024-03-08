from rest_framework import serializers

    
    
class Info_Bulk_Posting_Serializer(serializers.Serializer):
    news_links = serializers.CharField()
    website_id = serializers.CharField(max_length=500)
    category = serializers.CharField(max_length=500, required=False, allow_blank=True)
    post_status = serializers.CharField(max_length=200)
    img_status = serializers.CharField(max_length=200)

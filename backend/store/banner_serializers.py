from rest_framework import serializers
from .media_urls import serialized_media_url
from .models import Banner
class BannerSerializer(serializers.ModelSerializer):
    desktop_image=serializers.SerializerMethodField();mobile_image=serializers.SerializerMethodField()
    class Meta:model=Banner;fields=['id','placement','eyebrow','title','description','desktop_image','mobile_image','image_alt','primary_button_label','primary_button_link','secondary_button_label','secondary_button_link','theme','object_position','sort_order']
    def absolute(self,file_field):
        return serialized_media_url(file_field, self.context)
    def get_desktop_image(self,obj):return self.absolute(obj.desktop_image)
    def get_mobile_image(self,obj):return self.absolute(obj.mobile_image)

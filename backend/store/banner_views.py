from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .banner_serializers import BannerSerializer
from .models import Banner
class BannerListView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request):
        now=timezone.now();placement=request.query_params.get('placement','hero');banners=Banner.objects.filter(active=True,placement=placement).filter(Q(starts_at__isnull=True)|Q(starts_at__lte=now)).filter(Q(ends_at__isnull=True)|Q(ends_at__gte=now))
        response = Response(BannerSerializer(banners,many=True,context={'request':request}).data)
        # Banner uploads are admin-managed content; never let a browser or CDN
        # keep serving an older banner after an edit.
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

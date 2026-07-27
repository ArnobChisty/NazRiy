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
        now=timezone.now();placement=request.query_params.get('placement','hero');banners=Banner.objects.filter(active=True,placement=placement).filter(Q(starts_at__isnull=True)|Q(starts_at__lte=now)).filter(Q(ends_at__isnull=True)|Q(ends_at__gte=now));return Response(BannerSerializer(banners,many=True,context={'request':request}).data)

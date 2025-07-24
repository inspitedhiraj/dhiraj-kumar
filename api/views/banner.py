from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from tannis_app.serializer import *
from tannis_app.models import *

@api_view(['GET'])
def bannerDetails(request):
    banner = Banner.objects.all()
    p = BannerSerializer(banner, many=True)
    return Response(p.data)
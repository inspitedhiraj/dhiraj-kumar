from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from tannis_app.serializer import *
from tannis_app.models import *

@api_view(['GET'])
def category(request):
    category = Category.objects.filter(status=True)
    c = CategorySerializer(category, many=True)
    return Response(c.data)

@api_view(['GET'])
def onOurRadar(request):
    category = Category.objects.filter(on_our_radar=True, status=True)
    c = CategorySerializer(category, many=True)
    return Response(c.data)
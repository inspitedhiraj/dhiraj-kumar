from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from tannis_app.serializer import *
from tannis_app.models import *

@api_view(['GET'])
def midCategory(request, category):
    if request.method == 'GET':
        midCategory = MidCategory.objects.filter(status=True, category=category)
        s = MidCategorySerializer(midCategory, many=True)
        return Response(s.data)
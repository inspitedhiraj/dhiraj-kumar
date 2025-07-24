from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from tannis_app.serializer import *
from tannis_app.models import *

@api_view(['GET'])
def subCategory(request, mid_category):
    if request.method == "GET":
        subCategory = SubCategory.objects.filter(mid_category=mid_category, status=True)
        s = SubCategorySerializer(subCategory, many=True)
        return Response(s.data)
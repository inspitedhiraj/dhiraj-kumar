
from tannis_app.models import *
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from tannis_app.serializer import *
from rest_framework.response import Response

@api_view(['GET'])
def brand(request):
    brand = Brand.objects.all()
    serialized = BrandSerializer(brand, many=True)
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Brand retrieved successfully",
        "data": serialized.data
    }
    return Response(response_data)
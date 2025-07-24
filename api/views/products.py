
from tannis_app.models import *
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from tannis_app.serializer import *
from rest_framework.response import Response
from rest_framework import status

# @api_view(['GET'])
# def product(request):
#     product = Product.objects.filter(status=True)
#     serialized_products = ProductSerializer(product, many=True)
    # Wrap the serialized data in an object
    # response_data = {
    #     "status": "success",
    #     "message": "Product retrieved successfully",
    #     "data": serialized_products.data
    # }
    # return Response(response_data)

@api_view(['GET'])
def product(request, sub_category):
    if request.method == "GET":
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        cart_data = CartSerializer(cart).data
        product_status = {}

        for variant in Variant.objects.all():
            product_id = variant.product.id
            if product_id not in product_status:
                status = 'not_in_cart'
                quantity_in_cart = next((item.qty for item in cart_items if item.variant == variant), 0)
                if quantity_in_cart > 0:
                    status = 'in_cart'
                product_status[product_id] = {
                    'product_id': variant.product.id,
                    'product_name': variant.product.p_name,
                    'status': status,
                    'quantity_in_cart': quantity_in_cart,
                }

        return Response(product_status)

@api_view(['GET'])
def variantByMidCategory(request, mid_category):
    if request.method == "GET":
        variant = Variant.objects.filter(product__mid_category=mid_category, product__status=True)
        v = VariantSerializer(variant, many=True, context={"request":request})
        return Response(v.data)

@api_view(['GET'])
def variantDetails(request, variantId):
    if request.method =="GET":
        variant = Variant.objects.filter(id=variantId, product__status=True)
        serialized = VariantDetailsSerializer(variant, many=True, context={"request":request})
        response_data = {
            "status": "success",
            "message": "Product details retrieved successfully",
            "data": serialized.data
        }
        return Response(response_data)

# @api_view(['GET'])
# def productImageDetails(request):
#     image = Product_image.objects.filter(status=True)
#     serialized = ImageSerializer(image, many=True)
    # Wrap the serialized data in an object
    # response_data = {
    #     "status": "success",
    #     "message": "Product details retrieved successfully",
    #     "data": serialized.data
    # }
    # return Response(response_data)

@api_view(['GET'])
def wishlist(request):
    variant = Variant.objects.filter(product__status=True, product__product_type='wishlist')
    serialized_product_details = WishlistSerializer(variant, many=True)
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Wishlist product retrieved successfully",
        "data": serialized_product_details.data
    }
    return Response(response_data)

@api_view(['GET'])
def trandingOffer(request):
    tranding_offer = TrandingOffer.objects.filter()
    serialized = TrandingOfferSerializer(tranding_offer, many=True)
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Tranding offer retrieved successfully",
        "data": serialized.data
    }
    return Response(response_data)

@api_view(['GET'])
def trending(request):
    product = Product.objects.filter(status=True, trending=1)
    serialized = ProductSerializer(product, many=True)
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Trending product retrieved successfully",
        "data": serialized.data
    }
    return Response(response_data)

@api_view(['GET'])
def dealsOfTheDay(request):
    product = Product.objects.filter(status=True, deals_of_the_day=1)
    serialized = DealsOfTheDaySerializer(product, many=True)
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Deals of the day product retrieved successfully",
        "data": serialized.data
    }
    return Response(response_data)

@api_view(['GET'])
def mostPopular(request):
    product = Product.objects.filter(status=True, most_popular=1)
    serialized = MostPopularSerializer(product, many=True, context={"request":request})
    # Wrap the serialized data in an object
    response_data = {
        "status": "success",
        "message": "Most popular product retrieved successfully",
        "data": serialized.data
    }
    return Response(response_data)

@api_view(['GET'])
def searchProduct(request):
    if request.method == "GET":
        sub_category = request.query_params.get('sub_category')
        brand = request.query_params.get('brand')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        discount = request.query_params.get('discount')
        variant = Variant.objects.filter(product__status=True)
    
        if sub_category is not None:
            variant = variant.filter(product__sub_category=sub_category)
        
        if brand is not None:
            variant = variant.filter(product__brand=brand)
        
        if min_price is not None and max_price is not None:
            variant = variant.filter(product__mrp__gte = min_price, product__mrp__lte = max_price)
        
        if discount is not None:
            variant = variant.filter(product__discount=discount)
        
        serialized = VariantSerializer(variant, many=True)
        # Wrap the serialized data in an object
        response_data = {
            "status": "success",
            "message": "Product retrieved successfully",
            "items" : len(serialized.data),
            "data": serialized.data
        }
        return Response(response_data)

@api_view(['POST'])
def moreLike(request):
    if request.method == "POST":
        if 'product_id' not in request.data:
            return Response({
                "status": "error",
                "message": "product_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        product_id = request.data['product_id']
        variant = Variant.objects.filter(product_id=product_id, product__status=True)
        v = VariantSerializer(variant, many=True)
        return Response(v.data)
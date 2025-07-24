from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from tannis_app.models import *
from tannis_app.serializer import *
from django.shortcuts import render
# import requests
import json
from collections import defaultdict
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrder(request):
    if request.method == 'GET':
        user = request.user
        order = Order.objects.filter(customer=user)
        order_serializer = GetOrderSerializer(order, many=True)
        return Response(order_serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order(request):
    if request.method == 'POST':
        
        customer = request.user
        if not Cart.objects.filter(user=customer).exists():
            return Response({"message":"Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def shippingAddress(request):
    if request.method == 'POST':
        
        pin_code = request.data.get('pin_code')
        if not DeliveryZone.objects.filter(pin_code=pin_code).exists():
            return Response({"deliverable": False, "message": "We do not deliver to this pin code."}, status=404)
            
        serializer = ShippingAddressSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            data = serializer.save()
            return Response({
                'status': 'success',
                'Message': 'Shipping Address updated successfully.',
            })
        else:
            return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetShippingAddress(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    shipping_address = ShippingAddress.objects.filter(customer=profile)
    s = ShippingAddressSerializer(shipping_address, many=True)
    return Response(s.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def CheckOut(request):
    if request.method == 'GET':
        user = request.user
        total_price = 0
        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.filter(cart=cart)
        for item in cart_item:
            total_price = item.price*item.qty
        
        return Response({
            "cart": cart,
            "total_price": total_price
        })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def make_default_shipping_address(request, shipping_id):
    # user = User.objects.get(user=request.user)
    profile = Profile.objects.get(user=request.user)
    try:
        # return Response(shipping_id)
        address = ShippingAddress.objects.get(id=shipping_id, customer=profile)
    except ShippingAddress.DoesNotExist:
        return Response({'error': 'Address not found'}, status=404)

    ShippingAddress.objects.filter(customer=profile).update(is_default=False)
    shipping_address = ShippingAddress.objects.get(id=shipping_id)
    shipping_address.is_default = True
    shipping_address.save()
    return Response({"status":"success", "message":"Status changed."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDefaultShippingAddress(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    shipping_address = ShippingAddress.objects.get(customer=profile, is_default=True)
    s = ShippingAddressSerializer(shipping_address, many=False)
    return Response(s.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reviewOrderDetails(request):
    if request.method == 'GET':
        user = request.user
        
        if user:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({"Status":"Error", "message":"Cart Not found."})
        
        cart_items = CartItem.objects.filter(cart=cart).select_related('variant')
        serializer = CartItemSerializer(cart_items, many=True, context={'request': request})

        grouped_data = defaultdict(list)
        for item in serializer.data:
            delivery_date = str(item['delivery_date'])
            grouped_data[delivery_date].append(item)
        
        serialized = reviewOrderSerializer(cart)
        
        profile = Profile.objects.get(user=user)
        shipping_address = ShippingAddress.objects.filter(customer=profile, is_default=1).first()
        address = ShippingAddressSerializer(shipping_address, many=False)
        response = {
            "message":"Data retrive Successfully.",
            "data":grouped_data, "shipping_address":address.data,
            "total_mrp":serialized.data['total_mrp'],
            "total_discount":serialized.data['total_discount'],
            "total_amount":serialized.data['total_price']
        }
        return Response(response)
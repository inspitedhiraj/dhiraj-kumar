from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from tannis_app.serializer import *
from tannis_app.models import *
from rest_framework import status
import uuid

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def addToCart(request):
    if request.user.is_authenticated:
        user = request.user
        session_id = None
    else:
        user = None
        session_id = request.session.get('session_id', None)

        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id

    variant_id = request.data.get('variant')
    quantity = int(request.data.get('quantity', 1))
    
    try:
        variant = Variant.objects.get(id=variant_id)
    except Variant.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if user:
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user, total_price=0)
    else:
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(session_id=session_id, total_price=0)

    try:
        cart_item = CartItem.objects.get(cart=cart, variant=variant)
        cart_item.qty = quantity
        cart_item.total_price = cart_item.qty*variant.product.selling_price
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart,
            variant=variant,
            p_name=variant.product.p_name,
            thumbnail=variant.thumbnail,
            mrp=variant.product.mrp,
            price=variant.product.selling_price,
            qty=quantity,
            total_price=variant.product.selling_price
        )
    
    cart.total_price = sum(item.total_price for item in cart.carts.all())
    cart.save()

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def removeFromCart(request, variant):
    if request.user.is_authenticated:
        user = request.user
        session_id = None
    else:
        user = None
        session_id = request.session.get('session_id', None)

        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
    
    try:
        variant = Variant.objects.get(id=variant)
    except Variant.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if user:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, variant=variant)
        cart_item.delete()
    except CartItem.DoesNotExist:
        return Response({"Message": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        

    return Response({"status":"success", "message":"Product from cart deleted successfully."})

@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def updateCartQty(request):
    if request.user.is_authenticated:
        user = request.user
        session_id = None
    else:
        user = None
        session_id = request.session.get('session_id', None)

        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id

    variant_id = request.data.get('variant')
    quantity = request.data.get('qty')
    
    try:
        variant = Variant.objects.get(id=variant_id)
    except Variant.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if user:
        cart = Cart.objects.get(user=user)
    else:
        cart = Cart.objects.get(session_id=session_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, variant=variant)
        cart_item.qty = int(quantity)
        cart_item.total_price = cart_item.qty * cart_item.price
        cart_item.save()
    except CartItem.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    cart.total_price = sum(item.total_price for item in cart.carts.all())
    cart.save()

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getCart(request):
    if request.method == 'GET':
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.get('session_id') if not user else None
        
        if user:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({"detail": "Cart Not found."}, status=status.HTTP_404_NOT_FOUND)
        elif session_id:
            try:
                cart = Cart.objects.get(session_id=session_id)
            except Cart.DoesNotExist:
                return Response({"detail": "Cart Not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "User Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serialized = CartSerializer(cart)
        return Response({"message":"Cart item retrive Successfully.", "data":serialized.data})
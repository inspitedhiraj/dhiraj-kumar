from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework import serializers
from tannis_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import datetime
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db import transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'c_name', 'image']

class MidCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MidCategory
        fields = ['id', 'm_name', 'image']

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 's_name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'p_name', 'mrp', 'discount', 'selling_price', 'product_type', 'brand', 'short_description', 'long_description', 'product_type', 'slug', 'sub_category', 'mid_category', 'category']

class VariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    delivery_date= serializers.SerializerMethodField()
    is_added_to_cart = serializers.SerializerMethodField()
    class Meta:
        model = Variant
        fields = '__all__'
    
    def get_is_added_to_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            cart = Cart.objects.get(user=user)
            return CartItem.objects.filter(cart=cart, variant=obj).exists()
        return False
    
    def get_delivery_date(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            base_shipping_days = obj.base_shipping_days
            profile = Profile.objects.get(user=user)
            shipping_address = ShippingAddress.objects.get(customer=profile)
            delivery_zone = DeliveryZone.objects.get(pin_code=shipping_address.pin_code)
            extra_days = delivery_zone.extra_days
            delivery_days = base_shipping_days + extra_days
            return timezone.now().date() + timedelta(days=delivery_days)
        else:
            base_shipping_days = obj.base_shipping_days
            return timezone.now().date() + timedelta(days=base_shipping_days)

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class DealsOfTheDaySerializer(serializers.ModelSerializer):
    first_variant_image = serializers.SerializerMethodField()
    first_variant_size = serializers.SerializerMethodField()
    first_variant_id = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'p_name', 'mrp', 'discount', 'selling_price', 'product_type', 'brand', 'short_description', 'long_description', 'product_type', 'slug', 'sub_category', 'mid_category', 'category', 'first_variant_image', 'first_variant_size', 'first_variant_id']
    
    def get_first_variant_image(self, obj):
        first_variant = obj.variants.first()
        if first_variant and first_variant.thumbnail:
            return first_variant.thumbnail.url
        return None
    
    def get_first_variant_size(self, obj):
        first_variant = obj.variants.first()
        if first_variant and first_variant.size:
            return first_variant.size
        return None
    
    def get_first_variant_id(self, obj):
        first_variant = obj.variants.first()
        if first_variant and first_variant.id:
            return first_variant.id
        return None

class VariantDetailsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    images = ImageSerializer(many=True)
    delivery_date= serializers.SerializerMethodField()
    class Meta:
        model = Variant
        fields = '__all__'
    
    def get_delivery_date(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            base_shipping_days = obj.base_shipping_days
            profile = Profile.objects.get(user=user)
            shipping_address = ShippingAddress.objects.get(customer=profile)
            delivery_zone = DeliveryZone.objects.get(pin_code=shipping_address.pin_code)
            extra_days = delivery_zone.extra_days
            delivery_days = base_shipping_days + extra_days
            return timezone.now().date() + timedelta(days=delivery_days)
        else:
            base_shipping_days = obj.base_shipping_days
            return timezone.now().date() + timedelta(days=base_shipping_days)

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = []

class SignUpSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

    def create(self, validated_data):
        email_or_phone = validated_data['email_or_phone']
        otp = random.randint(1000, 9999)
        user = ''
        
        phone_validator = RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be in the format: '+999999999'."
            )
        
        try:
            phone_validator(email_or_phone)
            phone = email_or_phone
            username = phone
            email = ''
        except:
            email = email_or_phone
            username = email
            phone = ''
        
        # try:
        #     subject = "OTP for verification"
        #     message = "Your OTP: " + str(otp)
        #     sender = settings.EMAIL_HOST_USER
        #     receiver = validated_data['email']
        #     mail = EmailMessage(subject, message, sender,[receiver])
        #     mail.send(fail_silently=False)
        # except Exception as e:
        #     return {'details': str(e)}
        
        if email:
            try:
                user = User.objects.get(email=email)
            except:
                pass
        elif phone:
            try:
                profile = Profile.objects.get(phone=phone)
                user_id = profile.user_id
                user = User.objects.get(id=user_id)
            except:
                pass
        if user:
            profile = Profile.objects.get(user=user)
            profile.otp = otp
            profile.save()
        else:
            user = User(
                    username=username,
                    email=email
                    )
            user.save()
            profile = Profile(user=user, otp=otp, phone=phone, status=True)
            profile.save()
        cust_id = 'cust-' + str(user.id).zfill(4)
        data = {'user':user, 'id':user.id, 'otp':otp, 'customer-id':cust_id}
        return data

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

# class SignInSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
        
#         user = authenticate(username=username, password=password)
        
#         if user is None:
#             raise serializers.ValidationError("Invalid credential")
        
#         data['user'] = user
        
#         return data

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    class Meta:
        model = Variant
        fields = '__all__'

# class SignInSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
        
#         user = authenticate(username=username, password=password)
        
#         if user is None:
#             raise serializers.ValidationError("Invalid credential")
        
#         data['user'] = user
        
#         return data

class UpdateUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class UpdateProfileDetailsSerializer(serializers.ModelSerializer):
    user = UpdateUserDetailsSerializer(many=False)
    dob = serializers.DateField(input_formats=['%Y-%m-%d'])
    class Meta:
        model = Profile
        fields = ['dob', 'gender', 'user']
    
    def update(self, instance, data):
        user_data = data.pop('user')
        id = instance.user.id
        dob = data.get('dob')
        gender = data.get('gender')
        
        profile = Profile.objects.get(user_id=id)
        profile.gender = gender
        profile.dob = dob
        profile.save()
        
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        user = User.objects.get(id=id)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        return {"message":"Profile Updated successfully."}

class GetUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class GetProfileSerializer(serializers.ModelSerializer):
    user = GetUserDetailsSerializer(many=False)
    class Meta:
        model = Profile
        fields = ['id', 'phone', 'dob', 'gender', 'address', 'pin_code', 'city', 'state', 'image', 'user']

# class UpdateCustomerAddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ['address', 'city', 'state', 'pin_code']

class UpdateCustomerProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']

class CartItemSerializer(serializers.ModelSerializer):
    # item_total = serializers.SerializerMethodField()
    delivery_date= serializers.SerializerMethodField()
    is_added_to_cart = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'variant', 'p_name', 'thumbnail', 'price', 'qty', 'total_price', 'delivery_date', 'is_added_to_cart']
    
    # def get_item_total(self, obj):
    #     return obj.price * float(obj.qty)
    
    def get_is_added_to_cart(self, obj):
        return True
    
    def get_delivery_date(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            base_shipping_days = obj.variant.base_shipping_days
            profile = Profile.objects.get(user=user)
            shipping_address = ShippingAddress.objects.get(customer=profile, is_default=True)
            delivery_zone = DeliveryZone.objects.get(pin_code=shipping_address.pin_code)
            extra_days = delivery_zone.extra_days
            delivery_days = base_shipping_days + extra_days
            return timezone.now().date() + timedelta(days=delivery_days)
        else:
            base_shipping_days = obj.variant.base_shipping_days
            return timezone.now().date() + timedelta(days=base_shipping_days)

class CartSerializer(serializers.ModelSerializer):
    carts = CartItemSerializer(many=True)
    total_mrp = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'carts', 'total_price', 'total_mrp', 'total_discount']
    
    def get_total_price(self, obj):
        return sum([item.price * item.qty for item in obj.carts.all()])
    
    def get_total_mrp(self, obj):
        return sum([item.mrp * item.qty for item in obj.carts.all()])
    
    def get_total_discount(self, obj):
        total_price = sum([item.price * item.qty for item in obj.carts.all()])
        total_mrp = sum([item.mrp * item.qty for item in obj.carts.all()])
        return total_mrp-total_price

class TrandingOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrandingOffer
        fields = ['id', 'coupon', 'image', 'discount']

class VerifyOtpSerializer(serializers.Serializer):
    userId = serializers.CharField()
    otp = serializers.CharField()
    
    def create(self, data):
        id = data.get('userId')
        otp = data.get('otp')
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message":"User not found."})
        profile = Profile.objects.get(user=user)
        if profile.otp == otp:
            if user.is_active == False:
                user.is_active = True
            token, created = Token.objects.get_or_create(user=user)
            return token.key
        else:
            raise serializers.ValidationError({"message":"OTP mismatch."})

class otpEmailSerializer(serializers.Serializer):
    email = serializers.CharField()

    def create(self, validated_data):
        email = validated_data['email']
        otp = random.randint(1000, 9999)
        user = self.context['request'].user
        
        # try:
        #     subject = "OTP for verification"
        #     message = "Your OTP: " + str(otp)
        #     sender = settings.EMAIL_HOST_USER
        #     receiver = validated_data['email']
        #     mail = EmailMessage(subject, message, sender,[receiver])
        #     mail.send(fail_silently=False)
        # except Exception as e:
        #     return {'details': str(e)}
        
        USER = User.objects.filter(email=email).first()
        if not USER:
            otp = Otp(email=email, otp=otp, user=user.id)
            otp.save()
            data = {"message":"OTP sent successfully.", 'otp':otp.otp}
        else:
            data = {"message":"Email exist."}
        return data

class updateEmailSerializer(serializers.Serializer):
    # old_otp = serializers.CharField()
    otp = serializers.CharField()

    def create(self, validated_data):
        # old_otp = validated_data['old_otp']
        otp = validated_data['otp']
        user = self.context['request'].user.id
        
        t=1
        try:
            otp = Otp.objects.get(user=user, otp=otp)
        except:
            raise serializers.ValidationError({"status":"error", "message":"OTP mismatch"})
            t=0
        if t:
            USER = User.objects.get(id=user)
            USER.email = otp.email
            USER.save()
            
        data = {"message":"Email updated successfully."}
        return data

# class addEmailSerializer(serializers.Serializer):
#     new_otp = serializers.CharField()

#     def create(self, validated_data):
#         new_otp = validated_data['new_otp']
#         user = self.context['request'].user.id
        
#         USER = User.objects.get(id=user)
#         if USER.email == '':
#             t=1
#             try:
#                 otp = Otp.objects.get(user=user, otp=new_otp)
#             except:
#                 message = "OTP mismatch"
#                 t=0
#             if t:
#                 USER = User.objects.get(id=user)
#                 USER.email = otp.email
#                 USER.save()
#                 message = "Email updated successfully."
#         else:
#             raise serializers.ValidationError("Already Email added in your account.")
            
#         data = {"message":message}
#         return data

class otpPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def create(self, validated_data):
        phone = validated_data['phone']
        otp = random.randint(1000, 9999)
        user = self.context['request'].user
        
        phone_validator = RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be in the format: '+999999999'."
            )
        try:
            phone_validator(phone)
        except:
            raise serializers.ValidationError("Phone Number is not valid.")
        
        # try:
        #     subject = "OTP for verification"
        #     message = "Your OTP: " + str(otp)
        #     sender = settings.EMAIL_HOST_USER
        #     receiver = validated_data['email']
        #     mail = EmailMessage(subject, message, sender,[receiver])
        #     mail.send(fail_silently=False)
        # except Exception as e:
        #     return {'details': str(e)}
        
        profile = Profile.objects.filter(phone=phone).first()
        if not profile:
            otp = Otp(phone=phone, otp=otp, user=user.id)
            otp.save()
            data = {"message":"OTP sent successfully.", 'otp':otp.otp}
        else:
            data = {"message":"Phone number exist."}
        return data

class updatePhoneSerializer(serializers.Serializer):
    # old_otp = serializers.CharField()
    otp = serializers.CharField()

    def create(self, validated_data):
        # old_otp = validated_data['old_otp']
        otp = validated_data['otp']
        user = self.context['request'].user.id
        
        t=1
        try:
            otp = Otp.objects.get(user=user, otp=otp)
        except:
            raise serializers.ValidationError({"status":"error", "message":"OTP mismatch"})
            t=0
        if t:
            profile = Profile.objects.get(user_id = user)
            profile.phone = otp.phone
            profile.save()
            
        data = {"message":"Phone updated successfully."}
        return data

class OrderedItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ordered_item
        fields = ['id', 'variant', 'qty', 'price']

class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderedItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'payment_mode', 'payment_status', 'transaction_id', 'status', 'ordered_items']
        read_only_fields = ['total_amount', 'payment_status']

    def create(self, validated_data):
        customer = self.context['request'].user
        payment_mode = validated_data.get('payment_mode')
        
        cart = Cart.objects.get(user=customer)
        items = CartItem.objects.filter(cart=cart)
        
        with transaction.atomic():
            total_amount = sum(item.price * item.qty for item in items)
        
            order = Order.objects.create(customer=customer, total_amount=total_amount, payment_mode=payment_mode)
            for item in items:
                variant = item.variant
                qty = item.qty
                price = item.price
                
                if variant.qty < qty:
                    raise serializers.ValidationError({
                        "detail": f"Insufficient stock for {variant.product.p_name}."
                    })
                variant.qty = variant.qty - qty
                variant.save()

                Ordered_item.objects.create(
                    order=order,
                    variant=variant,
                    qty=qty,
                    price=price
                )
            cart.delete()
        return order

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'name', 'phone', 'address1', 'address2', 'city', 'state', 'pin_code', 'country', 'type_of_address', 'email', 'is_default']
    def create(self, validated_data):
        name = validated_data['name']
        address1 = validated_data['address1']
        address2 = validated_data['address2']
        city = validated_data['city']
        state = validated_data['state']
        pin_code = validated_data['pin_code']
        phone = validated_data['phone']
        country = validated_data['country']
        type_of_address = validated_data['type_of_address']
        email = validated_data['email']
        user = self.context['request'].user.id
        
        profile = Profile.objects.get(user=user)
        if ShippingAddress.objects.filter(customer=profile).exists():
            default = False
        else:
            default = True
        
        shipping_address = ShippingAddress(customer=profile, name=name, address1=address1, address2=address2, city=city, state=state, pin_code=pin_code, phone=phone, country=country, type_of_address=type_of_address, email=email, is_default=default)
        shipping_address.save()
        return shipping_address

class GetOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'payment_mode', 'transaction_id', 'payment_status', 'status', 'created_at']

class MostPopularVariantSerializer(serializers.ModelSerializer):
    is_added_to_cart = serializers.SerializerMethodField()
    class Meta:
        model = Variant
        fields = '__all__'
    
    def get_is_added_to_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if user and user.is_authenticated:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return False
            return CartItem.objects.filter(cart=cart, variant=obj).exists()
        return False

class MostPopularSerializer(serializers.ModelSerializer):
    variants = MostPopularVariantSerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'p_name', 'mrp', 'discount', 'selling_price', 'product_type', 'brand', 'short_description', 'long_description', 'product_type', 'slug', 'sub_category', 'mid_category', 'category', 'variants']

class reviewOrderSerializer(serializers.ModelSerializer):
    carts = CartItemSerializer(many=True)
    total_mrp = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_price', 'total_mrp', 'total_discount', 'carts']
    
    def get_total_price(self, obj):
        return sum([item.price * item.qty for item in obj.carts.all()])
    
    def get_total_mrp(self, obj):
        return sum([item.mrp * item.qty for item in obj.carts.all()])
    
    def get_total_discount(self, obj):
        total_price = sum([item.price * item.qty for item in obj.carts.all()])
        total_mrp = sum([item.mrp * item.qty for item in obj.carts.all()])
        return total_mrp-total_price
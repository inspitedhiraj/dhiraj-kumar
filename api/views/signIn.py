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
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# @api_view(['POST'])
# def signIn(request):
#     if request.method == 'POST':
#         data = request.data
#         serializer = SignInSerializer(data=data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             mail_response = serializer.validated_data['response']
#             try:
#                 profile = Profile.objects.get(user=user)
#             except Profile.DoesNotExist:
#                 return Response("Sorry, you are not user.")
#             if user and profile:
#                 token, created = Token.objects.get_or_create(user=user)
#                 if created:
#                     token = Token.objects.get(user=user)
#                 response = {'Message':'Loggedin successfully.', 'token_key':token.key, 'data':mail_response}
#                 return Response(response)
#             else:
#                 response = {'Message':'Username or password is incorrect.'}
#                 return Response(response)
#         else:
#             return Response(serializer.errors)

@api_view(['POST'])
def create_profile(request):
    if request.method == 'POST':

        email = request.data.get('email')
        
        serializer = SignUpSerializer(data=request.data)
        
        if serializer.is_valid():
            data=serializer.save()
            # user = User.objects.get(email=email)
            # token, created = Token.objects.get_or_create(user=user)
            # if created:
            #     token = Token.objects.get(user=user)
            return Response({
                'status': 'success',
                # 'Message': 'Profile created successfully',
                'userId': data['id'],
                'otp': data['otp'],
                'customer-id':data['customer-id'],
                # 'details': data['response']
            })
        else:
            return Response(serializer.errors, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserDetails(request):
    if request.method == 'PUT':
        user = request.user
        data = request.data
        profile = Profile.objects.get(user=user)
        if profile:
            serializer = UpdateProfileDetailsSerializer(profile, data=data, context={"request":request})
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "status":"success",
                    "message":"Customer details updated successfully.",
                }
                return Response(response_data)
            else:
                return Response(serializer.errors)
        else:
            return Response("Not a valid user")

@api_view(['GET', 'POST'])
def deleteUserDetails(request):
    if request.method == 'POST':
        user = request.POST.get('user-name')
        try:
            USER = User.objects.get(username=user)
        except User.DoesNotExist:
            CONTEXT = {"message":"User Not Found."}
            return render(request, 'delete-user.html', CONTEXT)
        USER.delete()
        CONTEXT = {"message":"User Deleted successfully."}
        return render(request, 'delete-user.html', CONTEXT)
    return render(request, 'delete-user.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCustomerDetails(request):
    if request.method == 'GET':
        user = request.user
        profile = Profile.objects.get(user=user)
        serialized_data = GetProfileSerializer(profile, many=False)
        response_data = {
            "status":"success",
            "message":"User details retrived successfully.",
            "data":serialized_data.data
        }
        return Response(response_data)

# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def updateCustomerAddress(request):
#     if request.method == 'PUT':
#         user = request.user
#         data = request.data
#         profile = Profile.objects.get(user=user)
#         if profile:
#             serializer = UpdateCustomerAddressSerializer(profile, data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 response = {
#                     "status":"success",
#                     "massage":"Address updated successfully."
#                 }
#                 return Response(response)
#             else:
#                 return Response(serializer.errors)
#         else:
#             return Response("Not a valid user")

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCustomerProfileImage(request):
    if request.method == 'PUT':
        user = request.user
        data = request.data
        profile = Profile.objects.get(user=user)
        if profile:
            serializer = UpdateCustomerProfileImageSerializer(profile, data=data)
            if serializer.is_valid():
                serializer.save()
                response = {
                    "status":"success",
                    "massage":"Profile image updated successfully."
                }
                return Response(response)
            else:
                return Response(serializer.errors)
        else:
            return Response("Not a valid user")

@api_view(['POST'])
def verifyOtp(request):
    if request.method == 'POST':

        user = request.data.get('userId')
        otp = request.data.get('otp')
        
        serializer = VerifyOtpSerializer(data=request.data)
        
        if serializer.is_valid():
            token_key = serializer.save()
            return Response({
                'status': 'success',
                'Message': 'Otp verified successfully',
                'token': token_key,
            })
        else:
            return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logOut(request):
    if request.method == 'POST':

        token_key = request.auth.key
        
        token = Token.objects.get(key=token_key)
        token.delete()
        
        return Response({
                'status': 'success',
                'Message': 'Logged out successfully',
            })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def otpEmail(request):
    if request.method == 'POST':
        
        serializer = otpEmailSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            data=serializer.save()
            return Response({
                'status': 'success',
                'data': data,
            })
        else:
            return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateEmail(request):
    if request.method == 'POST':
        
        serializer = updateEmailSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            data=serializer.save()
            return Response({
                'status': 'success',
                'data': data['message'],
            })
        else:
            return Response(serializer.errors, status=400)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def addEmail(request):
#     if request.method == 'POST':
        
#         serializer = addEmailSerializer(data=request.data, context={"request":request})
        
#         if serializer.is_valid():
#             data=serializer.save()
#             return Response({
                # 'status': 'success',
        #         'Message': data['message'],
        #     })
        # else:
        #     return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def otpPhone(request):
    if request.method == 'POST':
        
        serializer = otpPhoneSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            data=serializer.save()
            return Response({
                'status': 'success',
                'Message': data['message'],
                'otp':data['otp']
            })
        else:
            return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updatePhone(request):
    if request.method == 'POST':
        
        serializer = updatePhoneSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            data=serializer.save()
            return Response({
                'status': 'success',
                'Message': data['message'],
            })
        else:
            return Response(serializer.errors, status=400)
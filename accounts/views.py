from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer, OtpCodeSerializer, PassResetOtpCodeSerializer
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class SignupView(CreateAPIView):
    model = User
    serializer_class = SignupSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        token = Token.objects.create(user=user)
        self._token = token

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response(
            {
                "message": "User created successfully",
                "token": self._token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({
            "message": "User logout successfully",
        },
            status=status.HTTP_200_OK,
        )

class OtpRequestView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = OtpCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            otp = serializer.instance
            try:
                send_mail(
                    subject="Your Verification Code",
message=f"""
Hello {otp.user.username},

Your verification code is: {otp.code}

This code is valid for the next 6 minutes. Please use it to complete your action. 
If you did not request this, please ignore this email.

Thank you,
The Event Management Team
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[otp.user.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Unable to send email, {e}")
            return Response({
                "message": "OTP code sent successfully",
            },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpResetView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = PassResetOtpCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                send_mail(
                        subject="Your Password Has Been Reset",
message=f"""
Hello {user.username},

This is a confirmation that your account password has been successfully reset. 
If you did not request this change, please contact our support team immediately.

Thank you,
The Event Management Team
""",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False
                )
            except Exception as e:
                print(f"Unable to send email, {e}")
            return Response({
                "message": "Password reset successfully",
            },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


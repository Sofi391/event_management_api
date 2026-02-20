from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OtpCode
from random import randint
from django.utils import timezone
from datetime import timedelta


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField( write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password','password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        return data
    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError('Email cannot be empty')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already registered')
        return email


    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise serializers.ValidationError('Email or password is required')
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            raise serializers.ValidationError('User not found')
        if not user_obj.check_password(password):
            raise serializers.ValidationError('Incorrect password')

        data['user'] = user_obj
        return data


class OtpCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    # purpose = serializers.ChoiceField(choices=['reset','Signup'])

    class Meta:
        model = OtpCode
        fields = ('email',)
    def validate(self, data):
        email = data.get('email')
        if not email:
            raise serializers.ValidationError('Email cannot be empty')
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User not found')
        return data

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data['email']).first()
        # purpose = validated_data.get('purpose').lower()

        ran_otp = randint(100000,999999)
        otp, created = OtpCode.objects.update_or_create(
            user=user,
            # purpose=purpose,
            used = False,
            defaults = {'code': ran_otp,'created_at': timezone.now()}
        )
        return otp


class PassResetOtpCodeSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    def validate(self, data):
        otp_oj = OtpCode.objects.filter(code=data['otp'],used=False).first()
        password = data.get('password')
        password2 = data.get('password2')
        if not otp_oj:
            raise serializers.ValidationError('Invalid Or Used OTP')
        if timezone.now() - otp_oj.created_at > timedelta(minutes=6):
            raise serializers.ValidationError('OTP code expired,Please request a new one')
        if not password or not password2:
            raise serializers.ValidationError('Both password fields are required')
        if password != password2:
            raise serializers.ValidationError('Passwords do not match')
        self.user = otp_oj.user

        return data

    def save(self, **kwargs):
        user = self.user
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        OtpCode.objects.filter(user=user, code=self.validated_data['otp']).update(used=True)
        return user







from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


_MODEL_FIELD_NAMES = [f.name for f in User._meta.get_fields() if getattr(f, "concrete", True)]


def _intersect_fields(desired):
    return [f for f in desired if f in _MODEL_FIELD_NAMES]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User

        fields = _intersect_fields(("id", "username", "email", "last_name", "role", "password"))
        read_only_fields = _intersect_fields(("id",))

    def _generate_unique_username(self, base: str) -> str:

        base = base or "user"
        username = base
        suffix = 0
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base}{suffix}"
        return username

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        username = validated_data.pop("username", None)
        email = validated_data.get("email")


        if not username:
            if email:
                base = email.split("@")[0]
            else:

                raise serializers.ValidationError(
                    {"non_field_errors": ["Username or email is required."]}
                )
            username = self._generate_unique_username(base)


        extra_fields = {
            k: v
            for k, v in validated_data.items()
            if k not in ("email", "username")
            and k in _MODEL_FIELD_NAMES
        }


        user = User.objects.create_user(username=username, email=email, password=password, **extra_fields)
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User

        fields = _intersect_fields(("id", "username", "email", "first_name", "last_name", "role", "date_joined"))
        read_only_fields = _intersect_fields(("id", "email", "created_at"))

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():

            if attr in _MODEL_FIELD_NAMES:
                setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
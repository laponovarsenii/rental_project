from django.db import models
from django.conf import settings


class Listing(models.Model):

    HOUSING_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('room', 'Room'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    city = models.CharField(max_length=100)

    district = models.CharField(max_length=100, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    rooms = models.PositiveIntegerField()

    housing_type = models.CharField(
        max_length=100,
        choices=HOUSING_TYPES,
    )

    image = models.ImageField(upload_to='listings/', blank=True, null=True)

    address = models.CharField(max_length=255, blank=True)

    area = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    floor = models.PositiveSmallIntegerField(null=True, blank=True)

    pets_allowed = models.BooleanField(default=False)

    is_furnished = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    session_key = models.CharField(max_length=40, blank=True, null=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ViewHistory(models.Model):

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='view_history'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_listings'
    )

    session_key = models.CharField(max_length=40, null=True, blank=True)

    viewed_at = models.DateTimeField(auto_now_add=True)

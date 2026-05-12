from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from listings.models import Listing


class Review(models.Model):

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']
        unique_together = ('listing', 'author')

    def __str__(self):
        author_name = getattr(self.author, 'username', str(self.author))
        return f'{author_name} -> {self.listing.title} ({self.rating}★)'
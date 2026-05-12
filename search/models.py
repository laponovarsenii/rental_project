from django.db import models
from django.conf import settings




class SearchHistory(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )


    keyword = models.CharField(max_length=255)


    searched_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-searched_at']


    def __str__(self):
        return f'{self.user.name}: "{self.keyword}"'

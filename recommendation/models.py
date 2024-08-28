from django.db import models

class Recommendation(models.Model):
    stock_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_name} - {self.created_at}"

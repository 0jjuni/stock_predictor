from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class InterestStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=100)
    stock_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.stock_name} ({self.stock_code})"

from django.db import models
from django.utils import timezone

class Recommendation(models.Model):
    stock_name = models.CharField(max_length=100)
    stock_code = models.CharField(max_length=20)  # 주식 코드 추가
    created_at = models.DateField(default=timezone.now)  # 날짜만 저장

    def __str__(self):
        return f"{self.stock_name} ({self.stock_code}) - {self.created_at}"

from django.db import models

class minusPredict(models.Model):
    stock_name = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=255)
    prediction = models.FloatField()
    created_at = models.DateField()

    def __str__(self):
        return f"{self.stock_name} - {self.created_at}"



class Predict_5(models.Model):
    stock_name = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=255)
    prediction = models.FloatField()  # 기존 예측 결과
    created_at = models.DateField()  # 예측 날짜
    is_after_market_close = models.BooleanField(default=False)  # 15:30 이후 예측 여부 추가

    def __str__(self):
        return f"{self.stock_name} - {self.created_at}"

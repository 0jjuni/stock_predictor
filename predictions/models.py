from django.db import models

class minusPredict(models.Model):
    stock_name = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=255)
    prediction = models.FloatField()
    created_at = models.DateField()

    def __str__(self):
        return f"{self.stock_name} - {self.created_at}"
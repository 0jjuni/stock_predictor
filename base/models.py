from django.db import models

# Create your models here.


from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

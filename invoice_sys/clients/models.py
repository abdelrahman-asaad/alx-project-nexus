from django.db import models
from common.models import BaseModel

class Client(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    

    def __str__(self):
        return f"{self.company_name} - {self.name}"

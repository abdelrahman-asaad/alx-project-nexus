from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,        #to reffer to User model
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(class)s_created" #to adjust class name to related name such as : porduct_created ,
                                                                                 # invoice_created , etc 
    )

    class Meta:
        abstract = True
# abstract=True means django will not create this model in database but making it as common
#template for models     
# 
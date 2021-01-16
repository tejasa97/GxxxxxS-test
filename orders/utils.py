from django.db import models


class BaseModel(models.Model):
    """Base model with `created_date` and `modified_date` fields
    """

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

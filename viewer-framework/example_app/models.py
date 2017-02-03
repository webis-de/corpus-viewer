from django.db import models

class Example_Model(models.Model):
    name = models.CharField(max_length=30, unique=True)
    count_of_something = models.IntegerField(default=0)

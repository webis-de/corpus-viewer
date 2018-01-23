from django.db import models

class Example_Model(models.Model):
    name = models.CharField(max_length=30)
    count_of_something = models.IntegerField(default=0)
    corpus_viewer_tags = models.ManyToManyField('viewer.m_Tag', related_name='corpus_viewer_items')
    some_boolean_value = models.BooleanField()

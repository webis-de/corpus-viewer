from django.db import models

class m_Entity(models.Model):
    name = models.CharField(max_length=30, unique=True)

class m_Tag(models.Model):
    class Meta:
        ordering = ['name']
        
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    m2m_entity = models.ManyToManyField(m_Entity)

    def __str__(self):
        return '<Tag [%s]>' % (self.name)
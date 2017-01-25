from django.db import models

class Example_Model(models.Model):
    name = models.CharField(max_length=30, unique=True)
    count_of_something = models.IntegerField(default=0)

class m_Entity(models.Model):
    id_item = models.CharField(max_length=200, unique=True, db_index=True)

class m_Tag(models.Model):
    class Meta:
        ordering = ['name']
        
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    m2m_example_model = models.ManyToManyField(Example_Model, related_name='tags')
    m2m_entity = models.ManyToManyField(m_Entity, related_name='tags')

    def __str__(self):
        return '<Tag [%s]>' % (self.name)
from django.shortcuts import render
from django.http import JsonResponse
from example_app.models import *
import random
import string

def index(request):
	# Example_Model.objects.all().delete()
	if Example_Model.objects.count() == 0:
		list_objects = []
		for index in range(0, 10000):
			list_objects.append(
				Example_Model(
					name="".join( [random.choice(string.ascii_lowercase) for i in range(8)] ),
					count_of_something="".join( [random.choice(string.digits) for i in range(3)] ),
					some_boolean_value=random.choice([True, False])
				)
			)

		Example_Model.objects.bulk_create(list_objects)

	return JsonResponse({})
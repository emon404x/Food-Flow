from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Location


@login_required
def location_list_json(request):
    """
    Helper API returning existing active areas and cities for autocomplete or dropdown assistance.
    """
    areas = list(Location.objects.exclude(area='').values_list('area', flat=True).distinct().order_by('area'))
    cities = list(Location.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city'))
    return JsonResponse({'areas': areas, 'cities': cities})

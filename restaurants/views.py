from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Restaurant, Rating
from geopy import distance
from geopy.geocoders import Nominatim
from django.contrib import messages
from .forms import RestaurantForm, UserRegistrationForm
from django.http import JsonResponse
from rest_framework import generics
from .serializers import RestaurantSerializer


def restaurant_map(request):
    return redirect('http://localhost:3000/')


def filter_restaurants(fixed_location=(32.738167, -97.380900)):
    restaurants = Restaurant.objects.all()
    nearby_restaurants = []
    for restaurant in restaurants:
        if restaurant.latitude and restaurant.longitude:
            restaurant_location = (restaurant.latitude, restaurant.longitude)
            if distance.distance(fixed_location, restaurant_location).miles <= 2.5:
                nearby_restaurants.append(restaurant)
    return nearby_restaurants


class RestaurantList(generics.ListAPIView):
    serializer_class = RestaurantSerializer

    def list(self, request, *args, **kwargs):
        queryset = filter_restaurants()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        filtered_data = [{"name": item["name"], "latitude": item["latitude"], "longitude": item["longitude"],
                          "avg_rating": item["avg_rating"]} for item in data]
        return JsonResponse(filtered_data, safe=False)


def restaurant_list(request):
    nearby_restaurants = filter_restaurants()
    context = {'restaurants': nearby_restaurants}
    return render(request, 'restaurant_list.html', context)


def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    ratings = Rating.objects.filter(restaurant=restaurant)
    context = {'restaurant': restaurant, 'ratings': ratings}
    return render(request, 'restaurant_detail.html', context)


def restaurant_rating(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        value = int(request.POST['value'])
        user = request.user
        try:
            rating = Rating.objects.get(user=user, restaurant=restaurant)
            rating.value = value
            rating.save()
        except Rating.DoesNotExist:
            rating = Rating.objects.create(user=user, restaurant=restaurant, value=value)
            rating.save()
        ratings = Rating.objects.filter(restaurant=restaurant)
        avg_rating = ratings.aggregate(avg_rating=Avg('value'))['avg_rating']
        restaurant.avg_rating = avg_rating
        restaurant.save()
        return redirect('restaurant_detail', restaurant_id=restaurant.id)

    return render(request, 'restaurant_detail.html', {'restaurant': restaurant})


def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            restaurant_name = form.cleaned_data.get('name')
            restaurant = Restaurant.objects.filter(address=address).first()
            if restaurant:
                messages.warning(request, 'Restaurant already exists.')
            else:
                geolocator = Nominatim(user_agent="my-app-name")
                location = geolocator.geocode(address)
                restaurant = form.save(commit=False)
                if location:
                    restaurant.latitude = location.latitude
                    restaurant.longitude = location.longitude
                restaurant.save()
                messages.success(request, 'Restaurant added successfully.')
                return redirect('/')
    else:
        form = RestaurantForm()
    context = {'form': form}
    return render(request, 'add_restaurant.html', context)

from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

urlpatterns = [
    path('', restaurant_list, name='restaurant_list'),
    path('<int:restaurant_id>/', restaurant_detail, name='restaurant_detail'),
    path('<int:restaurant_id>/rating/', restaurant_rating, name='restaurant_rating'),
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='base.html'), name='logout'),
    path('add-restaurant/', add_restaurant, name='add_restaurant'),
    path('api/restaurants/', RestaurantList.as_view()),
    path('restaurant_map/', restaurant_map, name='restaurant_map'),
]

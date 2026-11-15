from django.contrib import admin
from .models import Vendor, Item, Dish, DishItem, Event, EventItem
admin.site.register(Vendor); admin.site.register(Item); admin.site.register(Dish); admin.site.register(DishItem); admin.site.register(Event); admin.site.register(EventItem)

from django.contrib import admin
from django.urls import path
from cater import views as v
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v.index, name='index'),
    path('vendors/', v.vendors_page, name='vendors_page'),
    path('items/', v.items_page, name='items_page'),
    path('dishes/', v.dishes_page, name='dishes_page'),
    path('events/', v.events_page, name='events_page'),
    path('events/<int:pk>/', v.event_detail_page, name='event_detail_page'),
    path('api/vendors/', v.api_vendors, name='api_vendors'),
    path('api/vendors/<int:pk>/', v.api_vendor_detail, name='api_vendor_detail'),
    path('api/items/', v.api_items, name='api_items'),
    path('api/items/<int:pk>/', v.api_item_detail, name='api_item_detail'),
    path('api/dishes/', v.api_dishes, name='api_dishes'),
    path('api/dishes/<int:pk>/', v.api_dish_detail, name='api_dish_detail'),
    path('api/events/', v.api_events, name='api_events'),
    path('api/events/<int:pk>/breakdown/', v.api_event_breakdown, name='api_event_breakdown'),
    path('vendor-items/', v.vendor_items_view, name='vendor_items'),
    path('vendor-items-api/', v.vendor_items_api, name='vendor_items_api'),
    path('api/events/<int:pk>/', v.api_event_detail)

]

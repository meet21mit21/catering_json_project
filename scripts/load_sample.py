from cater.models import Vendor, Item, Dish, DishItem, Event, EventItem
from decimal import Decimal
from django.utils.dateparse import parse_date
import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
data = json.load(open(BASE_DIR / 'sample_data.json','r'))
Vendor.objects.all().delete(); Item.objects.all().delete(); DishItem.objects.all().delete(); Dish.objects.all().delete(); EventItem.objects.all().delete(); Event.objects.all().delete()
vobjs=[]; 
for v in data['vendors']: vobjs.append(Vendor.objects.create(name=v['name'], mobile_number=v.get('mobile_number',''), address=v.get('address','')))
iobjs=[]; 
for i in data['items']: iobjs.append(Item.objects.create(name=i['name'], vendor=vobjs[i['vendor']-1], unit=i['unit']))
dobjs=[];
for d in data['dishes']:
    dish = Dish.objects.create(name=d['name'])
    for ing in d['ingredients']: DishItem.objects.create(dish=dish, item=iobjs[ing['item']-1], quantity=Decimal(ing['qty']))
    dobjs.append(dish)
for e in data['events']:
    ev = Event.objects.create(name=e['name'], date=parse_date(e['date']), number_of_persons=e['persons'])
    ev.dishes.add(*[dobjs[i-1] for i in e['dishes']])
    scale = Decimal(ev.number_of_persons)/Decimal(100)
    for d in ev.dishes.all():
        for di in d.ingredients.all(): EventItem.objects.create(event=ev, item=di.item, quantity=(di.quantity*scale), source=f"Dish: {d.name}")
    for di in e.get('direct_items', []): EventItem.objects.create(event=ev, item=iobjs[di['item']-1], quantity=Decimal(di['qty']), source='Direct')
print("Sample data loaded.")

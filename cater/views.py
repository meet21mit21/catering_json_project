from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from decimal import Decimal
import json
from .models import Vendor, Item, Dish, DishItem, Event, EventItem
from .utils import group_event_items_by_vendor

def index(request): return render(request,'index.html')
def vendors_page(request): return render(request,'vendors.html')
def items_page(request): return render(request,'items.html')
def dishes_page(request): return render(request,'dishes.html')
def events_page(request): return render(request,'events.html')
def event_detail_page(request, pk): return render(request,'event_detail.html', {'event_id': pk})

def json_body(request):
    try: return json.loads(request.body.decode('utf-8')) if request.body else {}
    except json.JSONDecodeError: return None

@csrf_exempt
def api_vendors(request):
    if request.method=='GET':
        data=[{'id':v.id,'name':v.name,'mobile_number':v.mobile_number,'address':v.address} for v in Vendor.objects.all()]
        return JsonResponse({'results':data})
    if request.method=='POST':
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        v=Vendor.objects.create(name=body.get('name',''), mobile_number=body.get('mobile_number',''), address=body.get('address',''))
        return JsonResponse({'id':v.id,'name':v.name,'mobile_number':v.mobile_number,'address':v.address}, status=201)
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_vendor_detail(request, pk):
    v=get_object_or_404(Vendor,pk=pk)
    if request.method=='GET':
        return JsonResponse({'id':v.id,'name':v.name,'mobile_number':v.mobile_number,'address':v.address})
    if request.method in ['PUT','PATCH']:
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        v.name=body.get('name',v.name); v.mobile_number=body.get('mobile_number',v.mobile_number); v.address=body.get('address',v.address); v.save()
        return JsonResponse({'id':v.id,'name':v.name,'mobile_number':v.mobile_number,'address':v.address})
    if request.method=='DELETE':
        v.delete(); return JsonResponse({'status':'deleted'})
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_items(request):
    if request.method=='GET':
        data=[{'id':i.id,'name':i.name,'unit':i.unit,'vendor':{'id':i.vendor.id,'name':i.vendor.name,'mobile_number':i.vendor.mobile_number,'address':i.vendor.address}} for i in Item.objects.select_related('vendor')]
        return JsonResponse({'results':data})
    if request.method=='POST':
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        vendor=get_object_or_404(Vendor, pk=body.get('vendor_id'))
        i=Item.objects.create(name=body.get('name',''), unit=body.get('unit','Kg'), vendor=vendor)
        return JsonResponse({'id':i.id,'name':i.name,'unit':i.unit,'vendor_id':i.vendor.id}, status=201)
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_item_detail(request, pk):
    i=get_object_or_404(Item, pk=pk)
    if request.method=='GET': return JsonResponse({'id':i.id,'name':i.name,'unit':i.unit,'vendor_id':i.vendor.id})
    if request.method in ['PUT','PATCH']:
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        if 'vendor_id' in body: i.vendor=get_object_or_404(Vendor, pk=body['vendor_id'])
        i.name=body.get('name',i.name); i.unit=body.get('unit',i.unit); i.save()
        return JsonResponse({'id':i.id,'name':i.name,'unit':i.unit,'vendor_id':i.vendor.id})
    if request.method=='DELETE': i.delete(); return JsonResponse({'status':'deleted'})
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_dishes(request):
    if request.method=='GET':
        data=[]
        for d in Dish.objects.all():
            ingredients=[{'item_id':di.item.id,'item_name':di.item.name,'vendor_name':di.item.vendor.name,'vendor_mobile':di.item.vendor.mobile_number,'vendor_address':di.item.vendor.address,'quantity':str(di.quantity),'unit':di.item.unit} for di in d.ingredients.select_related('item__vendor')]
            data.append({'id':d.id,'name':d.name,'ingredients':ingredients})
        return JsonResponse({'results':data})
    if request.method=='POST':
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        from decimal import Decimal
        d=Dish.objects.create(name=body.get('name',''))
        for ing in body.get('ingredients', []):
            item=get_object_or_404(Item, pk=ing['item_id']); DishItem.objects.create(dish=d, item=item, quantity=Decimal(str(ing.get('quantity','0'))))
        return JsonResponse({'id':d.id,'name':d.name}, status=201)
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_dish_detail(request, pk):
    d=get_object_or_404(Dish, pk=pk)
    if request.method=='GET':
        ings=[{'id':di.id,'item_id':di.item.id,'item_name':di.item.name,'quantity':str(di.quantity),'unit':di.item.unit} for di in d.ingredients.select_related('item')]
        return JsonResponse({'id':d.id,'name':d.name,'ingredients':ings})
    if request.method in ['PUT','PATCH']:
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        from decimal import Decimal
        d.name=body.get('name',d.name); d.save()
        if 'ingredients' in body:
            d.ingredients.all().delete()
            for ing in body['ingredients']:
                item=get_object_or_404(Item, pk=ing['item_id']); DishItem.objects.create(dish=d, item=item, quantity=Decimal(str(ing.get('quantity','0'))))
        return JsonResponse({'id':d.id,'name':d.name})
    if request.method=='DELETE': d.delete(); return JsonResponse({'status':'deleted'})
    return HttpResponseBadRequest('Unsupported method')

@csrf_exempt
def api_events(request):
    if request.method=='GET':
        data=[{'id':e.id,'name':e.name,'date':e.date.isoformat(),'number_of_persons':e.number_of_persons} for e in Event.objects.all().order_by('-date')]
        return JsonResponse({'results':data})
    if request.method=='POST':
        body=json_body(request); 
        if body is None: return HttpResponseBadRequest('Invalid JSON')
        e=Event.objects.create(name=body.get('name',''), date=parse_date(body.get('date')), number_of_persons=int(body.get('number_of_persons',100)))
        dish_ids = body.get('dishes', [])
        if dish_ids: e.dishes.add(*Dish.objects.filter(id__in=dish_ids))
        scale = Decimal(e.number_of_persons)/Decimal(100)
        for d in e.dishes.all():
            for di in d.ingredients.select_related('item'):
                EventItem.objects.create(event=e, item=di.item, quantity=(di.quantity*scale), source=f"Dish: {d.name}")
        for entry in body.get('direct_items', []):
            item=get_object_or_404(Item, pk=entry['item_id']); qty=Decimal(str(entry.get('quantity','0')))
            EventItem.objects.create(event=e, item=item, quantity=qty, source='Direct')
        return JsonResponse({'id':e.id,'name':e.name}, status=201)
    return HttpResponseBadRequest('Unsupported method')


def event_to_json(e):
    return {
        "id": e.id,
        "name": e.name,
        "date": e.date,
        "number_of_persons": e.number_of_persons,
        "dishes": [
            {
                "id": d.id,
                "name": d.name,
                "ingredients": [
                    {
                        "item_id": di.item.id,
                        "item_name": di.item.name,
                        "quantity": float(di.quantity),
                        "unit": di.item.unit,
                        "vendor_name": di.item.vendor.name,
                        "vendor_number": di.item.vendor.mobile_number,
                        "vendor_address": di.item.vendor.address,
                    }
                    for di in d.ingredients.select_related("item__vendor")
                ],
            }
            for d in e.dishes.all()
        ],
    }


def api_event_detail(request, pk):
    e = get_object_or_404(Event, pk=pk)

    if request.method == "GET":
        return JsonResponse(event_to_json(e))

    if request.method in ["PUT", "PATCH"]:
        import json
        try:
            body = json.loads(request.body)
        except:
            return HttpResponseBadRequest("Invalid JSON")

        if "name" in body:
            e.name = body["name"]
        if "date" in body:
            e.date = parse_date(body["date"])
        if "number_of_persons" in body:
            e.number_of_persons = int(body["number_of_persons"])
        e.save()

        if "dishes" in body:
            e.dishes.set(Dish.objects.filter(id__in=body["dishes"]))
            e.event_items.filter(source__startswith="Dish:").delete()
            scale = Decimal(e.number_of_persons) / Decimal(100)
            for d in e.dishes.all():
                for di in d.ingredients.select_related("item"):
                    EventItem.objects.create(
                        event=e,
                        item=di.item,
                        quantity=(di.quantity * scale),
                        source=f"Dish: {d.name}",
                    )
        if "direct_items" in body:
            e.event_items.filter(source="Direct").delete()
            for entry in body["direct_items"]:
                item = get_object_or_404(Item, pk=entry["item_id"])
                qty = Decimal(str(entry.get("quantity", "0")))
                EventItem.objects.create(event=e, item=item, quantity=qty, source="Direct")

        return JsonResponse(event_to_json(e))

    if request.method == "DELETE":
        e.delete()
        return JsonResponse({"status": "deleted"})

    return HttpResponseBadRequest("Unsupported method")


def api_event_breakdown(request, pk):
    e=get_object_or_404(Event, pk=pk)
    groups, totals = group_event_items_by_vendor(e)
    header={'event_name':e.name,'date':e.date.isoformat(),'number_of_persons':e.number_of_persons}
    return JsonResponse({'header':header,'vendors':groups,'totals':totals})

def vendor_items_view(request):
    """Initial page with dropdown + date filter UI."""
    vendors = Vendor.objects.all().order_by('name')
    return render(request, 'vendor_items.html', {'vendors': vendors})


def vendor_items_api(request):
    """
    AJAX endpoint:
    /vendor-items-api/?vendor_id=1&start=2025-09-01&end=2025-09-30
    Returns data grouped by event.
    """
    vendor_id = request.GET.get('vendor_id')
    start = request.GET.get('start')
    end = request.GET.get('end')

    qs = (
        EventItem.objects
        .select_related('event', 'item')
        .filter(item__vendor_id=vendor_id,
                event__date__range=[start, end])
        .order_by('event__date')
    )

    grouped = defaultdict(list)
    for ei in qs:
        key = (ei.event.name, ei.event.date.strftime('%Y-%m-%d'))
        grouped[key].append({
            'item_name': ei.item.name,
            'quantity': str(ei.quantity),
            'unit': ei.item.unit,
        })

    results = []
    for (event_name, event_date), items in grouped.items():
        results.append({
            'event_name': event_name,
            'event_date': event_date,
            'items': items
        })

    return JsonResponse({'results': results})
from decimal import Decimal
from collections import defaultdict
def group_event_items_by_vendor(event):
    groups=[]; vendor_map=defaultdict(list); totals_by_vendor={}
    for ei in event.event_items.select_related('item__vendor','item').all():
        v=ei.item.vendor; vendor_map[v.id].append(ei)
    for vid, items in vendor_map.items():
        v = items[0].item.vendor; rows=[]; total_qty=Decimal('0')
        for ei in items:
            rows.append({'item_name':ei.item.name,'dish_name':ei.source.replace('Dish: ','') if ei.source.startswith('Dish:') else '','quantity':str(ei.quantity),'unit':ei.item.unit})
            total_qty += ei.quantity
        groups.append({'vendor':{'name':v.name,'mobile_number':v.mobile_number,'address':v.address},'items':rows})
        totals_by_vendor[v.name]=str(total_qty)
    return groups, totals_by_vendor

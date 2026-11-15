from django.db import models
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=12, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    def __str__(self): return self.name
class Item(models.Model):
    name = models.CharField(max_length=100)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='items')
    unit = models.CharField(max_length=10, default='Kg')
    def __str__(self): return self.name
class Dish(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name
class DishItem(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredients')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # per 100 ppl
class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    number_of_persons = models.IntegerField(default=100)
    dishes = models.ManyToManyField(Dish, blank=True)
    def __str__(self): return self.name
class EventItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=100, default='', blank=True)

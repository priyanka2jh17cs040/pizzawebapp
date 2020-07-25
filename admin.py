from django.contrib import admin
from .models import Item_Category, Item, Topping

# Register your models here.
admin.site.register(Item_Category)
admin.site.register(Item)
admin.site.register(Topping)
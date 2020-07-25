from django.db import models
from django.contrib.auth.models import User

# Models for admins.
class Topping(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Item_Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Item(models.Model):
    TYPE = [
        ('R', 'Regular Pizza'),
        ('S', 'Sicilian Pizza')
    ]
    category = models.ForeignKey(Item_Category, on_delete=models.CASCADE, related_name='item_category')
    name = models.CharField(max_length=64)
    item_type = models.CharField(max_length=1, choices=TYPE, blank=True, null=True)
    price_small = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def max_topping(self):
        if(self.name[0].isdigit()):
            string = ''
            for i in range(1, int(self.name[0]) +1):
                string += f'{i}'
            return string
        return None

    def __str__(self):
        if self.item_type != None:
            return f'{self.name} - {self.category} [{self.get_item_type_display()}]'
        else:
            return f'{self.name} - {self.category}'

# Internal Models
class Order(models.Model):
    STATUS = [
        ('Initiated', 'Initiated'),
        ('Completed', 'Completed'),
        ('Refunded', 'Refunded')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=64, choices=STATUS, default='Initiated')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __str__(self):
        return f'[ {self.status} ] Order #{self.pk} Amount: ${self.total} by {self.user} | {self.date}'

class Order_Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_detail = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    topping = models.ManyToManyField(Topping, blank=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

class Cart_Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='card_id')
    item_detail = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_details')
    size = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    topping = models.ManyToManyField(Topping, related_name='item_toppings', blank=True)

    def __str__(self):
        return f'Id #{self.pk} Item: {self.item_detail} Size: {self.size} Price: {self.price} '



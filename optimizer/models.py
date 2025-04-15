from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('A', 'High Value'),
        ('B', 'Medium Value'),
        ('C', 'Low Value'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    demand = models.IntegerField()
    supply = models.IntegerField()
    cost = models.IntegerField()
    selling_price = models.IntegerField(default=0)  # Added for profit calculation
    lead_time = models.IntegerField(default=7)  # Days for delivery
    safety_stock = models.IntegerField(default=0)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='B')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def profit_margin(self):
        if self.selling_price > 0 and self.cost > 0:
            return ((self.selling_price - self.cost) / self.selling_price) * 100
        return 0

    @property
    def reorder_point(self):
        return (self.demand * self.lead_time / 30) + self.safety_stock
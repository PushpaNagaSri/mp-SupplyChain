from django import forms

class SupplyChainForm(forms.Form):
    name = forms.CharField(label='Product Name', max_length=100, 
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    demand = forms.IntegerField(label='Demand (units/month)', 
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    supply = forms.IntegerField(label='Current Inventory', 
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    cost = forms.IntegerField(label='Cost per Unit (₹)', 
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))
    selling_price = forms.IntegerField(label='Selling Price (₹)', required=False,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    lead_time = forms.IntegerField(label='Lead Time (days)', required=False, initial=7,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    safety_stock = forms.IntegerField(label='Safety Stock', required=False, initial=0,
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(label='Inventory Category',
                               choices=[('A', 'High Value'), ('B', 'Medium Value'), ('C', 'Low Value')],
                               widget=forms.Select(attrs={'class': 'form-control'}))
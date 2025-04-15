from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import SupplyChainForm
from .models import Product
import pulp
import csv

# Auth Views (unchanged)
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if len(password1) >= 8:
                try:
                    user = User.objects.create_user(username=username, password=password1)
                    login(request, user)
                    return redirect('home')
                except Exception as e:
                    messages.error(request, 'Username already exists.')
            else:
                messages.error(request, 'Password must be at least 8 characters long.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

# Main Optimization View (updated)
@login_required
def optimize_view(request):
    if request.method == 'POST':
        form = SupplyChainForm(request.POST)
        if form.is_valid():
            # Save product
            product = Product(
                user=request.user,
                name=form.cleaned_data['name'],
                demand=form.cleaned_data['demand'],
                supply=form.cleaned_data['supply'],
                cost=form.cleaned_data['cost'],
                selling_price=form.cleaned_data['selling_price'] or 0,
                lead_time=form.cleaned_data['lead_time'] or 7,
                safety_stock=form.cleaned_data['safety_stock'] or 0,
                category=form.cleaned_data['category']
            )
            product.save()
            return redirect('optimize')
    else:
        form = SupplyChainForm()

    # Prepare product data with new features
    products = Product.objects.filter(user=request.user)
    total_value = sum(p.supply * p.cost for p in products)
    total_profit = sum((p.selling_price - p.cost) * p.supply for p in products if p.selling_price > 0)
    
    # ABC Analysis calculation
    abc_analysis = {
        'A': {'count': 0, 'value': 0},
        'B': {'count': 0, 'value': 0},
        'C': {'count': 0, 'value': 0}
    }
    
    for product in products:
        abc_analysis[product.category]['count'] += 1
        abc_analysis[product.category]['value'] += product.supply * product.cost

    product_data = []
    for product in products:
        difference = product.demand - product.supply
        urgency = (product.demand / product.supply) * product.cost if product.supply > 0 else float('inf')
        
        product_data.append({
            'id': product.id,
            'name': product.name,
            'demand': product.demand,
            'supply': product.supply,
            'cost': product.cost,
            'selling_price': product.selling_price,
            'profit_margin': product.profit_margin,
            'reorder_point': product.reorder_point,
            'category': product.get_category_display(),
            'difference': difference,
            'absolute_difference': abs(difference),
            'urgency': urgency,
            'status': "LOW" if product.supply < product.demand else "OK"
        })

    # Sort by urgency
    product_data.sort(key=lambda x: x['urgency'], reverse=True)

    return render(request, 'optimize.html', {
        'form': form,
        'products': product_data,
        'total_value': total_value,
        'total_profit': total_profit,
        'abc_analysis': abc_analysis
    })
# New CSV Export View
@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product', 'Category', 'Demand', 'Supply', 'Reorder Point', 
                    'Cost', 'Selling Price', 'Profit Margin', 'Status', 'Urgency'])
    
    products = Product.objects.filter(user=request.user)
    for product in products:
        status = "LOW" if product.supply < product.demand else "OK"
        urgency = (product.demand / product.supply) * product.cost if product.supply > 0 else float('inf')
        profit_margin = ((product.selling_price - product.cost) / product.selling_price * 100) if product.selling_price > 0 else 0
        writer.writerow([
            product.name,
            product.get_category_display(),
            product.demand,
            product.supply,
            product.reorder_point,
            product.cost,
            product.selling_price,
            f"{profit_margin:.2f}%",
            status,
            f"{urgency:.2f}"
        ])
    
    return response

# New Quick Reorder View
@login_required
def quick_reorder(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    product.supply = product.demand
    product.save()
    return redirect('optimize')

# Existing CRUD Views (unchanged)
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
    return redirect('optimize')

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        form = SupplyChainForm(request.POST)
        if form.is_valid():
            product.name = form.cleaned_data['name']
            product.demand = form.cleaned_data['demand']
            product.supply = form.cleaned_data['supply']
            product.cost = form.cleaned_data['cost']
            product.save()
            return redirect('optimize')
    else:
        form = SupplyChainForm(initial={
            'name': product.name,
            'demand': product.demand,
            'supply': product.supply,
            'cost': product.cost
        })
    return render(request, 'update_product.html', {'form': form})
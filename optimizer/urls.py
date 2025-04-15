from django.contrib import admin
from django.urls import path
from optimizer import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),  # Root URL points to auth_view
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),  # Home page
    path('optimize/', views.optimize_view, name='optimize'),  # Optimization page
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update/<int:product_id>/', views.update_product, name='update_product'),
    path('signup/', views.signup_view, name='signup'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('quick-reorder/<int:product_id>/', views.quick_reorder, name='quick_reorder'),
]

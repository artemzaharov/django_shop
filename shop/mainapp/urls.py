from django.urls import path
from .views import test_view, ProductDetailView

urlpatterns = [
    path('', test_view, name='base'),
    #ct_model and slug from models.py  def get_product_url(obj, viewname):
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail')
]



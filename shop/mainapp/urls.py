from django.urls import path
from .views import BaseView, ProductDetailView, CategoryDetailView

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    # ct_model and slug from models.py  def get_product_url(obj, viewname):
    path('products/<str:ct_model>/<str:slug>/',
         ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(),
         name='category_detail'),


]

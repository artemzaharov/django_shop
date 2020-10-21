from django.shortcuts import render
from django.views.generic import DetailView
from .models import Notebook, Smartphone, Category


def test_view(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    return render(request, 'base.html', {'categories': categories})


class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }

    # we use view method dispatch to find model and get queryset(we used it because of ct_models)
    def dispatch(self, request, *args, **kwargs):
        # here we take ct_model from url
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # model = Model
    # queryset = Model.objects.all()

    # context_object_name It's just a human-understandable name of variable to access from templates 
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'


class CategoryDetailView(DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'
from django.shortcuts import render
from django.views.generic import DetailView, View
from .models import BackUpStorage, Design, Category, LatestProducts, Customer, Cart
from .mixins import CategoryDetailMixin


class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categoties_for_sidebar()  # to refer a category template
        products = LatestProducts.objects.get_products_for_main_page('backupstorage', 'design')
        context = {
            'categories': categories,
            'products': products,
        }
        return render(request, 'base.html', context)


# ---------------------VIEW_INFO_ABOUT_DIFFERENT_MODELS----------------------------------------------------------------

class ProductDetailView(CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {
        'design': Design,
        'backupstorage': BackUpStorage,
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'


class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'


class CartView(View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(owner=customer)
        categories = Category.objects.get_categoties_for_sidebar()
        context = {
            'cart': cart,
            'categories': categories,
        }
        return render(request, 'cart.html', context)
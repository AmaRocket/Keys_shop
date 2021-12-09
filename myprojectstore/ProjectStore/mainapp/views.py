from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import BackUpStorage, Design, Category, LatestProducts, Customer, Cart, CartProduct
from .mixins import CategoryDetailMixin, CartMixin


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categoties_for_sidebar()  # to refer a category template
        products = LatestProducts.objects.get_products_for_main_page('backupstorage', 'design')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart,
        }
        return render(request, 'base.html', context)


# ---------------------VIEW_INFO_ABOUT_DIFFERENT_MODELS----------------------------------------------------------------

class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
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

    # add model content_type(template for rendering product info)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'


# Add to basket
class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):  # redirect to endpoint (busket)
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')  # get wanted values from kwargs
        content_type = ContentType.objects.get(model=ct_model)  # define product model
        product = content_type.model_class().objects.get(slug=product_slug)  # get our product from content_type
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )  # create new cart_product objects with necessary arguments
        if created:
            self.cart.products.add(cart_product)
        self.cart.save()
        messages.add_message(request, messages.INFO, "Product Add To Basket Successfully")
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):  # Delete products fro basket

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')  # get wanted values from kwargs
        content_type = ContentType.objects.get(model=ct_model)  # define product model
        product = content_type.model_class().objects.get(slug=product_slug)  # get our product from content_type
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Product Remove From Basket Successfully")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')  # get wanted values from kwargs
        content_type = ContentType.objects.get(model=ct_model)  # define product model
        product = content_type.model_class().objects.get(slug=product_slug)  # get our product from content_type
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Quantity Changed Successfully")
        return HttpResponseRedirect('/cart/')


# Basket View
class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categoties_for_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories,
        }
        return render(request, 'cart.html', context)

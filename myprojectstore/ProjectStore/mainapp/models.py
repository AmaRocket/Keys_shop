from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


def get_models_for_count(*model_names):  # count balance of category models
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


# realization different models in one

class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__.meta.model_name.startswith(with_respect_to),
                                  reverse=True)
        return products


class LatestProducts:  # imitate model, but not enter to db

    objects = LatestProductsManager


class CategoryManager(models.Manager):
    # dict with actually info balane of category models
    CATEGORY_NAME_COUNT_NAME = {
        'BackUpStorage': 'backupstorage__count',
        'Design': 'design__count',
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categoties_for_sidebar(self):  # use annotation instrument
        models = get_models_for_count('design', 'backupstorage')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data  # return actually info about balance of category product


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Category Name')  # name of category
    slug = models.SlugField(unique=True)  # endpoint of url category
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    class Meta:
        abstract = True  # use Meta for sceleton of our product

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE, null=True)  # relation mto
    name = models.CharField(max_length=255, verbose_name='Product Name')  # name of product
    slug = models.SlugField(unique=True)  # endpoint of url product
    image = models.ImageField(verbose_name='Image Of Product')  # image of product
    description = models.TextField(verbose_name='Desciption Of Product', null=True)  # description of product
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')  # price of product

    def __str__(self):
        return self.name

    def get_model_name(self):
        return self.__class__.__name__.lower()


# ---------------------------PRODUCT-CATEGORIES---------------------------------------------------------------------------------

class BackUpStorage(Product):
    description = models.TextField(verbose_name='Desciption Of Product BackUp/Storage',
                                   null=True)  # description of product
    system_requirements = models.CharField(max_length=255, verbose_name='System Requirments')  # system requirments
    important_details = models.CharField(max_length=255, verbose_name='Important Details')  # important details
    terms = models.CharField(max_length=255, verbose_name='Terms')  # terms
    how_it_works = models.CharField(max_length=255, verbose_name='How It Works')  # how it works

    def __str__(self):
        return "{} : {}".format(self.category.name, self.name)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Design(Product):
    description = models.TextField(verbose_name='Desciption Of Product ',
                                   null=True)  # description of product
    system_requirements = models.CharField(max_length=255, verbose_name='System Requirments')  # system requirments
    reviews = models.CharField(max_length=255, verbose_name='Reviews')  # rewievs

    def __str__(self):
        return "{} : {}".format(self.category.name, self.name)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# -----------------------END_OF_CATEGORIES------------------------------------------------------------------------------

# ------------------------BASKET-----------------------------------------------------------------------------------------

class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)  # relation user-customer
    cart = models.ForeignKey('Cart', verbose_name='Busket', on_delete=models.CASCADE,
                             related_name='related_products')  # buscket
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # show all models in admin page
    object_id = models.PositiveIntegerField()  # id instanse of this model
    content_object = GenericForeignKey('content_type', 'object_id')  #
    qty = models.PositiveIntegerField(default=1)  # number od products
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total Price')  # total price

    def __str__(self):
        return "Product {} (For Busket)".format(self.content_object.name)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__._meta.model_name


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Owner', on_delete=models.CASCADE)  # owner of basket
    products = models.ManyToManyField(CartProduct, blank=True,
                                      related_name='related_cart')  # relation mtm with products
    total_product = models.PositiveIntegerField(default=0)  # numbers of products in basket
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2,
                                      verbose_name='Total Price')  # total $ in basket
    in_order = models.BooleanField(default=False)  # when customer make order basket will registered for it
    for_anonymous_user = models.BooleanField(default=False)  # pass key for non-registered users

    def __str__(self):
        return str(self.id)


# --------------------------END_OF_BASKET_SETTINGS----------------------------------------------------------------------


# --------------------------CUSTOMER_AND_ORDERS----------------------------------------------------------------------

class Customer(models.Model):
    user = models.OneToOneField(User, verbose_name='User', on_delete=models.CASCADE)  # relations customer-user
    phone = models.CharField(max_length=13, verbose_name='Phone Number', null=True, blank=True)  # phone number
    address = models.CharField(max_length=255, verbose_name='Address', null=True, blank=True)  # address
    orders = models.ManyToManyField('Order', verbose_name='Customer Orders',
                                    related_name='related_order')  # hystory of customer orders

    def __str__(self):
        return "Customer: {} {}".format(self.user.first_name, self.user.last_name)


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    # BUYING_TYPE_SELF = 'self'
    # BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'NEW'),
        (STATUS_IN_PROGRESS, 'IN PROGRESS'),
        (STATUS_READY, 'READY'),
        (STATUS_COMPLETED, 'COMPLETED')
    )

    # BUYING_TYPE_CHOICES = (
    #     (BUYING_TYPE_SELF, 'Pick Up'),
    #     (BUYING_TYPE_DELIVERY, 'Delivery')
    # )

    customer = models.ForeignKey(Customer, verbose_name='Customer', related_name='related_orders',
                                 on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Name')
    last_name = models.CharField(max_length=255, verbose_name='Last Name')
    phone = models.CharField(max_length=20, verbose_name='Telephone')
    cart = models.ForeignKey(Cart, verbose_name='Basket', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Address', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Order Status',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    # buying_type = models.CharField(
    #     max_length=100,
    #     verbose_name='Order Type',
    #     choices=BUYING_TYPE_CHOICES,
    #     default=BUYING_TYPE_SELF
    # )
    comment = models.TextField(verbose_name='Order Comment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Date Order Creating ')
    order_date = models.DateField(verbose_name='Date Order Receipt', default=timezone.now)

    def __str__(self):
        return str(self.id)

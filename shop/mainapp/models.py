from django.db import models
# take user model from django
from django.contrib.auth import get_user_model
# we import this for our Specifications model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    # this function help to build url to all models(smartphone,notebook) to show them in one template product_detail.html
    # obj is product(smart,note) and viewname is name in our urls.py
    ct_model = obj.__class__._meta.model_name
    # ._meta.model_name is lowercase name of model
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:
    # this is our custom queryset
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        # we give in args models
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        # we find content type with model name notebook
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_models in ct_models:
            # we call parent class of our ct_model
            model_products = ct_models.model_class(
            )._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            # this is used for some products to be first
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        # ._meta.model_name is lowercase name of model
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products


class LatestProducts:
    # LatestProducts.objects.get_products_for_main_page('smartphone', 'notebook', with_respect_to='notebook')
    objects = LatestProductsManager()

# Create your models here.

class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки':'notebook__count',
        'Смартфоны':'smartphone__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        # we cant use category.product.count for two modles notebook and smartphone because of content_type
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models).values())
        return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]
        


class Category(models.Model):
    """ Категории товаров """
    name = models.CharField(max_length=255, verbose_name="Имя категории")
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name


class Product(models.Model):
    """ Продукт """

    # this model wouldn't apear in migrations, it can be only Parent
    class Meta:
        abstract = True

    category = models.ForeignKey(
        Category, verbose_name="Категория", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Наименование")
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title


class Notebook(Product):

    diagonal = models.CharField(max_length=255, verbose_name="Диагональ")
    display_type = models.CharField(max_length=255, verbose_name="Тип дисплея")
    processor_freq = models.CharField(
        max_length=255, verbose_name="Частота процессора")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    video = models.CharField(max_length=255, verbose_name="ВидеоКарта")
    time_without_charge = models.CharField(
        max_length=255, verbose_name="Время работы аккумулятора")

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        # 'product_detail' is name in our urls.py
        return get_product_url(self, 'product_detail')


class Smartphone(Product):

    diagonal = models.CharField(max_length=255, verbose_name="Диагональ")
    display_type = models.CharField(max_length=255, verbose_name="Тип дисплея")
    resolution = models.CharField(
        max_length=255, verbose_name="Разрешение экрана")
    accum_volume = models.CharField(
        max_length=255, verbose_name="Объем батареи")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    sd = models.BooleanField(default=True, verbose_name='Наличие SD карты')
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Максимальный объем встраиваймой памяти")
    main_cam_mp = models.CharField(
        max_length=255, verbose_name="Главная камера")
    frontal_cam_mp = models.CharField(
        max_length=255, verbose_name="Фронтальная камера")

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    # @property
    # def sd(self):
    #     if self.sd:
    #         return 'Да'
    #     return 'Нет'


class CartProduct(models.Model):
    """ Продукт в корзине """
    user = models.ForeignKey(
        'Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина',
                             on_delete=models.CASCADE, related_name='related_products')
    # https://djbook.ru/rel3.0/ref/contrib/contenttypes.html
    # used for ForeignKey not to 1 model but to all models in our project in our case(Notebook,Smartphone)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Общая Цена')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.content_object.title)


class Cart(models.Model):
    """ Корзина """
    owner = models.ForeignKey(
        'Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(
        CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Общая Цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    """ Покупатель """
    user = models.ForeignKey(
        User, verbose_name='Владелец', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)

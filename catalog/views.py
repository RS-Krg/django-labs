from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Brand, Category, Product

PRODUCTS_PER_PAGE = 8
SORT_OPTIONS = {
    'name': ('name', 'По названию'),
    'cheap': ('price', 'Сначала дешёвые'),
    'expensive': ('-price', 'Сначала дорогие'),
    'new': ('-created_at', 'Сначала новые'),
}


def product_list(request, category_slug=None):
    category = None
    products = Product.objects.filter(is_active=True).select_related('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    brand = request.GET.get('brand', '')
    size = request.GET.get('size', '').strip()
    if brand:
        products = products.filter(brand__slug=brand)
    if size:
        products = products.filter(variants__size__iexact=size, variants__stock__gt=0).distinct()
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(search_index__contains=query.lower())
    sort = request.GET.get('sort', 'name')
    if sort not in SORT_OPTIONS:
        sort = 'name'
    products = products.order_by(SORT_OPTIONS[sort][0])
    page = Paginator(products, PRODUCTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'catalog/product_list.html', {
        'category': category, 'page': page, 'query': query, 'sort': sort,
        'sort_options': SORT_OPTIONS, 'categories': Category.objects.all(),
        'brands': Brand.objects.all(), 'brand': brand, 'size': size,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    return render(request, 'catalog/product_detail.html', {
        'product': product, 'categories': Category.objects.all(),
    })

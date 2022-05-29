import json
import math
from turtle import title
from django.views import generic
from django.http import JsonResponse


from product.models import (Variant,Product,ProductVariant,ProductImage,ProductVariantPrice)



def create_product(data, product):
    for image_url in data['product_image']:
        product_image = ProductImage(product=product, file_path=image_url)
        product_image.save()

    for product_variants in data['product_variant']:
        variant = Variant.objects.get(id=product_variants['option'])
        for product_variant_title in product_variants['tags']:
            product_variant_obj = ProductVariant(variant_title=product_variant_title, variant=variant, product=product)
            product_variant_obj.save()

    for product_variant_price in data['product_variant_prices']:
        title_list = product_variant_price['title'].split('/')
        product_variant_price_obj = ProductVariantPrice(product=product, price=product_variant_price['price'],
                                                        stock=product_variant_price['stock'])

        product_variant_one = ProductVariant.objects.filter(product=product, variant_title=title_list[0]).first()
        product_variant_price_obj.product_variant_one = product_variant_one
        product_variant_two = ProductVariant.objects.filter(product=product, variant_title=title_list[1]).first()
        product_variant_price_obj.product_variant_two = product_variant_two
        product_variant_three = ProductVariant.objects.filter(product=product, variant_title=title_list[2]).first()
        product_variant_price_obj.product_variant_three = product_variant_three

        product_variant_price_obj.save()

    response = {
        'status': 201,
        'detail': 'Product Created Successfully!'
    }

    return response

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    
    def post(self, request):

        try:
            data = json.loads(request.body)
            product = Product(title = data['title'], sku = data['sku'], description = data['description'])
            product.save()

            response = create_product(data,product)
        except Exception as e:
            response = {
                'status':400,
                'message': 'something went wrong! Try again'
            
            }
        return JsonResponse(response)


class ProductLsitView(generic.ListView):
    model = Product
    template_name = 'products/list.html'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductLsitView, self).get_context_data(**kwargs)
        context['variants'] = Variant.objects.all().distinct()
        return context

    def get_queryset(self):
        data = super().get_queryset()
        query = {}
        title = self.request.GET.get('title')
        p_from = self.request.GET.get('price_from')
        p_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')
        variant = self.request.GET.get('variant')

        if title:
            query['title__icontains'] = title
        query['productvariantprice__price__range'] = [p_from if p_from else 0, p_to if p_to else math.inf]
        if date:
            query['created_at__date'] = date
        if variant:
            query['productvariant__id'] = variant
        return data.filter(**query).distinct()


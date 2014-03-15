from os import environ, path
from random import choice, randint
import sys

sys.path.append(path.abspath('freezing'))
environ['DJANGO_SETTINGS_MODULE'] = 'freezing.settings'

from shame.models import Store, Product

with open('/usr/share/dict/words') as d:
    words = [word.strip() for word in d.readlines() if 3 <= len(word) < 12]

while True:
    subdomain = choice(words).lower()
    if len(Store.objects.filter(subdomain=subdomain)) == 0:
        break

store = Store(subdomain=subdomain)
store.save()

print('Created {} store'.format(store))

for _ in range(randint(3, 10)):
    product = Product(store=store, name=choice(words), price=randint(99,1000))
    product.save()

products = [str(product)
            for product in list(Product.objects.filter(store=store))]
print('Added {} and {}'.format(', '.join(products[:-1]), products[-1]))

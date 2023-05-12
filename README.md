# Digital shop

An example of a digital shop using a session based cart.

## Installation

Execute the following commands:
* ``pip intall -r requirements.txt``
* ``cd dj_shop``
* ``python manage.py migrate``
* ``python mange.py runserver``

By default the project uses its own example database. The instances 
are also stored in fixtures in app_goods/fixtures and app_users/fixtures.

The app_goods app also contains the following commands to quickly fill the 
database with the example data:

* ``python manage.py add_shops`` to add new shops
* ``python manage.py add_items`` to add new items
* ``python manage.py add_products`` to add new products
* ``python manage.py add_imgs`` to add new images for the products

The example data can be also added in the admin panel.

The credentials for the superuser are:

username: admin

password: 123456

The website goes with django-debug-toolbar, that can be turned off during the 
debug mode by commenting the following lines in settings.py:

````
INSTALLED_APPS = [
    ...
    'debug_toolbar',
    ...
    ]

````


````
MIDDLEWARE = [
    ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]
````

````
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

````

and in urls.py:

```
urlpatterns = [
    ...
    path('__debug__/', include(debug_toolbar.urls)),
    ...
]
```

The website uses the logging:

* every new login is saved in auth.log
* every new logout is saved in auth.log
* every new failed login is saved in auth.log
* every new balance adding is saved in auth.log
* every new status upgrading is saved in auth.log
* every new order creation is saved in order.log


The website is available in Russian and English.


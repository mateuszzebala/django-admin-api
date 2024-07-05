# Django Admin Page API

## Instalation

Run a command:

```bash 
pip install django-admin-page-api
```

Make changes in your project:

```py
# urls.py

from django_admin_page_api import sites

urlpatterns = [
    ...
    path('admin-api/', sites.urls),
    ...
]
```

```py
# settings.py

INSTALLED_APPS = [
    ...
    'django_admin_page_api',
    ...
]
```








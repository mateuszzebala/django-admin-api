# Django Admin Page API

[Django Admin Page API](https://pypi.org/project/django-admin-page-api/)

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

# Endpoints


## `/admin-api/`

- GET - Fetch list of models available in django admin

## `/admin-api/<app_label>/<model_name>`

- GET - Fetch model info 

- POST - Create new instance of model

## `/admin-api/<app_label>/<model_name>/items` 

- GET - List of items 
    - Search params:
        - offset
        - limit
        - query
        - sort
        - asc
- DELETE - Delete items
    - Request body:
        - keys - list of primary keys to delete (mey be separated by commas)

## `/admin-api/<app_label>/<model_name>/<pk>` 
- GET - Fetch item data
- PUT - Update instance of the object and save
- DELETE - Delete item

## `/admin-api/<app_label>/<model_name>/<pk>/<field_name>/`
- GET - get possible value to relation
    - Search params:
        - offset
        - limit
        - query
        - sort
        - asc

## `/admin-api/signin`
- Request body:
    - username
    - password

## `/admin-api/signout`

## `/admin-api/info`

- GET - Fetch current user and session data

## `/admin-api/csrf`

- GET - Fetch csrf token 

## `/admin-api/logs`

- GET - Fetch logs of authenticated user


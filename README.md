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

### Important: Data should be send using FormData

# Endpoints

## `/admin-api/`

- GET - Fetch list of models available in django admin

## `/admin-api/<app_label>/<model_name>`

- GET - Fetch model info

- POST - Create new instance of model (FormData)

## `/admin-api/<app_label>/<model_name>/<field_name>/autocomplete/`

- GET - get possible value to relation
  - Search params:
    - offset: number
    - limit: number
    - query: json string - e.g. {"int_field\_\_gt": 1}
    - sort: string
    - asc: boolean string

## `/admin-api/<app_label>/<model_name>/items`

- GET - List of items
  - Search params:
    - offset: number
    - limit: number
    - query: json string - e.g. {"int_field\_\_gt": 1}
    - sort: string
    - asc: boolean string
- DELETE - Delete items
  - Search params:
    - keys - list of primary keys to delete (may be separated by commas)

## `/admin-api/<app_label>/<model_name>/<pk>`

- GET - Fetch item data
- PUT - Update instance of the object and save (FormData)
- DELETE - Delete item

## `/admin-api/<app_label>/<model_name>/<pk>/<field_name>/autocomplete/`

- GET - get possible value to relation
  - Search params:
    - offset: number
    - limit: number
    - query: json string - e.g. {"int_field\_\_gt": 1}
    - sort: string
    - asc: boolean string

## `/admin-api/signin`

- POST - sign in (FormData)
  - Request body:
    - username: string
    - password: string

## `/admin-api/signout`

## `/admin-api/info`

- GET - Fetch current user and session data

## `/admin-api/csrf`

- GET - Fetch csrf token

## `/admin-api/logs`

- GET - Fetch logs of authenticated user

## `/admin-api/<app_label>/<model_name>/action/<action_code>/`

- POST - run model action
  - Request body:
    - keys - list of primary keys to delete (may be separated by commas)

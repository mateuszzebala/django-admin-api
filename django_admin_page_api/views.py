from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from .model_functions import *
from .utils import *
from django.contrib.auth import login, logout , authenticate
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.contrib.auth.models import Permission
import enum

def not_permitted():
    return JsonResponse({'message': 'You do not have permision to do this action!'})

class Actions(enum.Enum):
    VIEW = 'view'
    ADD = 'add'
    CHANGE = 'change'
    DELETE = 'delete'

def have_permission(request, admin_model, action):
    if not request.user.is_authenticated: return False
    if request.user.is_superuser: return True
    
    if action == Actions.VIEW:
        return admin_model.has_view_permission(request) 
    
    if action == Actions.ADD:
        return admin_model.has_add_permission(request) 
    
    if action == Actions.CHANGE:
        return admin_model.has_change_permission(request) 
    
    if action == Actions.DELETE:
        return admin_model.has_delete_permission(request) 
    
    return False
    
    

def index(request):
    models = get_all_models()
    return JsonResponse({
        'models': [get_model_json(model) for model in models]
    })

def signin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({'message': 'Authentication Successfull!'})
    else:
        return JsonResponse({'message': 'Authentication Failed!'})
    
def signout(request):
    logout(request)
    return JsonResponse({'message': 'Logout Succesfull!'})

class ModelView(View):
    
    http_method_names = [
        "get",
        "post",
    ]

    def get(self, request, app_label, model_name):
        
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        
        if have_permission(request, admin_model, Actions.VIEW):
            return JsonResponse({
                'model': get_model_json(model)
            })
        else: return not_permitted()
        
    def post(self, request, app_label, model_name):
        
        model = get_model_by_name(app_label, model_name)
        admin_model =get_admin_model_by_name(app_label, model_name)

        if have_permission(request, admin_model, Actions.ADD):
            item = create_new_item(model, request.POST, request.FILES)
            return JsonResponse({'item': item_to_json(item)})
        else: return not_permitted()
        
        

class ItemsView(View):
    
    http_method_names = [
        "get",
        "delete",
    ]
    
    def get(self, request, app_label, model_name):
        model = get_model_by_name(app_label, model_name)
        admin_model =get_admin_model_by_name(app_label, model_name)
        
        if not have_permission(request, admin_model, Actions.VIEW): return not_permitted()
        
        limit = int(request.GET.get('limit') or 100)
        offset = int(request.GET.get('offset') or 0)
        
        searchQuery = convert_query_object(request.GET.get('query', ''))
        queryError = False
        
        try:
            all_items = model.objects.filter(**searchQuery)
        except:
            queryError = True
            all_items = model.objects.all()
        
        sort = request.GET.get('sort') or 'pk'
        asc = False if request.GET.get('asc') == 'false' else True
        
        all_items = all_items.order_by(sort)
        
        if not asc: all_items = all_items.reverse()
        
        items = pagination(all_items, limit, offset)
        
        return JsonResponse({
            'length': len(all_items),
            'limit': limit,
            'offset': offset,
            'queryError': queryError,
            'items': [
                item_to_json(item) for item in items
            ]
        })

    def delete(self, request, app_label, model_name):
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.DELETE): return not_permitted()
        keys = convert_comma_array(request.GET.get('keys'))
        model.objects.filter(pk__in=keys).delete()
        return JsonResponse({'message': 'Items deleted succesfully!'})

class ItemView(View):
    
    http_method_names = [
        "get",
        "put",
        "delete",
    ]
    
    def get(self, request, app_label, model_name, pk):
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.VIEW): return not_permitted()
        item = model.objects.filter(pk=pk).first()
        
        if item is None:
            return JsonResponse({ 'item': None, })
        
        return JsonResponse({
            'item': item_to_json(item)
        })
        
    def put(self, request, app_label, model_name, pk):
        
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.CHANGE): return not_permitted()
        item = model.objects.filter(pk=pk).first()
        
        if item is None:
            return JsonResponse({ 'message': 'Item not found!', })
        
        item = update_item(model, item, request.POST, request.FILES)

        return JsonResponse({'item': item_to_json(item)})
        
    def delete(self, request, app_label, model_name, pk):
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.DELETE): return not_permitted()
        item = model.objects.filter(pk=pk).first()
        
        if item is None:
            return JsonResponse({ 'message': 'Item not found!', })

        return JsonResponse({'message': 'Item deleted succesfully!'})

def autocomplete(request, app_label, model_name, pk, field_name):
    
    model = get_model_by_name(app_label, model_name)
    admin_model = get_admin_model_by_name(app_label, model_name)
    if not have_permission(request, admin_model, Actions.VIEW): return not_permitted()
    
    item = model.objects.filter(pk=pk).first()
    item_field_value = getattr(item, field_name)
    
    field = None
    
    for fld in model._meta.get_fields():
        if fld.name == field_name:
            field = fld
            break
    
    if field is None:
        return JsonResponse({'message': 'Field not found!'})
    
    if not field.is_relation:
        return JsonResponse({
            'field': get_field_json(field),
        })

    related_model = field.related_model
    
    searchQuery = convert_query_object(request.GET.get('query', ''))
    limit = int(request.GET.get('limit') or 100)
    offset = int(request.GET.get('offset') or 0)
    sort = request.GET.get('sort') or 'pk'
    asc = False if request.GET.get('asc') == 'false' else True
    queryError = False
    
    try:
        all_items = related_model.objects.filter(**searchQuery)
    except:
        queryError = True
        all_items = related_model.objects.all()
    
    if field.requires_unique_target: 
        all_items = all_items.filter(Q(**{f'{field.remote_field.name}__isnull': True}) | Q(pk=item_field_value.pk if item_field_value is not None else None))
        
    items = all_items.order_by(sort)
    
    items = all_items[offset:offset+limit]   
    
    if not asc:
        items = items.reverse() 

    return JsonResponse({
        'field': get_field_json(field),
        'possible_values': dict((item.pk, str(item)) for item in items),
        'queryError': queryError
    })
    
def info(request):
    
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not authenticated!'})
    
    session = Session.objects.get(pk=request.session.session_key)
    
    return JsonResponse({
        'user': item_to_json(request.user)['fields'],
        'session': item_to_json(session)['fields']
    })

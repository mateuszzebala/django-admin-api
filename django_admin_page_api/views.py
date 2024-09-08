from django.http import JsonResponse
from django.views.generic import View
from .model_functions import *
from .utils import *
from django.contrib.auth import login, logout , authenticate
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.contrib.admin.models import LogEntry
from django.middleware.csrf import get_token
from django.http import QueryDict, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.encoding import force_str

def not_permitted():
    response = JsonResponse({'message': 'You do not have permision to do this action!'})
    response.status_code = 403
    return response

def put_data(func):
    def wrapper(self, request, *args, **kwargs):
        request.PUT = QueryDict('', mutable=True)
        
        if request.content_type == "application/x-www-form-urlencoded":
            request.PUT = QueryDict(force_str(request.body, encoding='utf-8'))
        elif request.content_type.startswith("multipart/form-data"):
            form_data, files = parse_multipart_data(request)
            request.PUT = form_data
            request.FILES.update(files)
        else:
            request.PUT = QueryDict('')
        
        return func(self, request, *args, **kwargs)
    return wrapper

@csrf_exempt
def index(request):
    
    if (not request.user.is_authenticated or not request.user.is_staff) and not request.user.is_superuser: return not_permitted()
    
    models: list[tuple] = get_all_models()
    return JsonResponse({
        'models': [add_some_json_to_model(get_model_json(model), admin_model, request, model) for model, admin_model in models]
    })  

@csrf_exempt
def signin(request):
    username = request.POST.get('username') or request.GET.get('username')
    password = request.POST.get('password') or request.GET.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({'message': 'Authentication Successfull!', 'sessionid': request.session.session_key})
    else:
        return JsonResponse({'message': 'Authentication Failed!'})
    
@csrf_exempt
def signout(request):
    logout(request)
    return JsonResponse({'message': 'Logout Succesfull!'})

@method_decorator(csrf_exempt, name='dispatch')
class ModelView(View):
    
    http_method_names = [
        "get",
        "post",
    ]

    def get(self, request, app_label, model_name):
        
        model, admin_model = get_model_with_admin(app_label, model_name)
        
        if have_permission(request, admin_model, Actions.VIEW):
            return JsonResponse({
                'model': add_some_json_to_model(get_model_json(model), admin_model, request, model)
            })
            
        else: return not_permitted()
        
    def post(self, request, app_label, model_name):
        
        model, admin_model = get_model_with_admin(app_label, model_name)

        if have_permission(request, admin_model, Actions.ADD):
            item, errors = create_new_item(model, request.POST, request.FILES)

            if item is not None:
                admin_model.log_addition(request, item, '')

            return JsonResponse({'item': item_to_json(item) if not len(errors) else None, 'errors': errors})
        
        else: return not_permitted()
        
        
@method_decorator(csrf_exempt, name='dispatch')
class ItemsView(View):
    
    http_method_names = [
        "get",
        "delete",
    ]
    
    def get(self, request, app_label, model_name):
        model, admin_model = get_model_with_admin(app_label, model_name)
        
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
        for key in keys:
            item = model.objects.filter(pk=key)
            if item:
                admin_model.log_deletion(request, item, '')
        return JsonResponse({'message': 'Items deleted succesfully!'})

@method_decorator(csrf_exempt, name='dispatch')
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
    
    @put_data
    def put(self, request, app_label, model_name, pk):
        
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.CHANGE): return not_permitted()
        item = model.objects.filter(pk=pk).first()
        
        if item is None:
            return JsonResponse({ 'message': 'Item not found!', })
        
        item, errors = update_item(model, item, request.PUT, request.FILES)

        admin_model.log_change(request, item, '')

        return JsonResponse({'item': item_to_json(item) if not len(errors) else None, 'errors': errors})
        
    def delete(self, request, app_label, model_name, pk):
        model = get_model_by_name(app_label, model_name)
        admin_model = get_admin_model_by_name(app_label, model_name)
        if not have_permission(request, admin_model, Actions.DELETE): return not_permitted()
        item = model.objects.filter(pk=pk).first()

        if item is None:
            return JsonResponse({ 'message': 'Item not found!', })
        
        admin_model.log_deletion(request, item, '')

        return JsonResponse({'message': 'Item deleted succesfully!'})

@csrf_exempt
def autocomplete_new(request, app_label, model_name, field_name):
    model, admin_model = get_model_with_admin(app_label, model_name)
    if not have_permission(request, admin_model, Actions.VIEW): return not_permitted()

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
    
    searchQuery = convert_query_object(request.GET.get('query', ''))
    limit = int(request.GET.get('limit') or 100)
    offset = int(request.GET.get('offset') or 0)
    sort = request.GET.get('sort') or 'pk'
    asc = False if request.GET.get('asc') == 'false' else True
    queryError = False

    related_model = field.related_model
    
    try:
        all_items = related_model.objects.filter(**searchQuery)
    except:
        queryError = True
        all_items = related_model.objects.all()
    
    if not field.many_to_many and field.requires_unique_target: 
        all_items = all_items.filter(**{f'{field.remote_field.name}__isnull': True})
        
    items = all_items.order_by(sort)
    
    items = all_items[offset:offset+limit]   
    
    if not asc:
        items = items.reverse() 

    return JsonResponse({
        'field': get_field_json(field),
        'possible_values': [
            {"pk": item.pk, "__str__": str(item)} for item in items
        ],
        'queryError': queryError
    })


@csrf_exempt
def autocomplete(request, app_label, model_name, pk, field_name):
    
    model, admin_model = get_model_with_admin(app_label, model_name)
    if not have_permission(request, admin_model, Actions.VIEW): return not_permitted()
    
    item = model.objects.filter(pk=pk).first()
    item_field_value = getattr(item, field_name)
    
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
    
    if not field.many_to_many and field.requires_unique_target: 
        all_items = all_items.filter(Q(**{f'{field.remote_field.name}__isnull': True}) | Q(pk=item_field_value.pk if item_field_value is not None else None))
        
    items = all_items.order_by(sort)
    
    items = all_items[offset:offset+limit]   
    
    if not asc:
        items = items.reverse() 

    return JsonResponse({
        'field': get_field_json(field),
        'possible_values': [
            {"pk": item.pk, "__str__": str(item)} for item in items
        ],
        'queryError': queryError
    })

@csrf_exempt
def info(request):
    
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not authenticated!'})
    
    session = Session.objects.get(pk=request.session.session_key)
    
    return JsonResponse({
        'user': item_to_json(request.user)['fields'],
        'session': item_to_json(session)['fields']
    })

@csrf_exempt
def logs(request):
    if (not request.user.is_authenticated or not request.user.is_staff) and not request.user.is_superuser: return not_permitted() 
    logs = LogEntry.objects.filter(user=request.user)
    return JsonResponse({
        'logs': [{
            'action': ['Add', 'Change', 'Delete',][log.action_flag - 1],
            'action_time': log.action_time,
            'change_message': log.change_message if log.change_message else [],
            'model': {
                'name': log.content_type.model_class().__name__,
                'app_label': log.content_type.app_label
            },
            'user': item_to_json(log.user)['fields']
        } for log in logs]
    })

@csrf_exempt
def csrf(request):
    return JsonResponse({
        'token': get_token(request)
    })
    
@csrf_exempt
def action(request, app_label: str, model_name: str, action_code: str):

    if request.method != 'POST':
        return JsonResponse({'message': 'Bad method!'})

    model, admin_model = get_model_with_admin(app_label, model_name)

    if not have_permission(request, admin_model, Actions.CHANGE): return not_permitted()

    keys = request.POST.get('keys').split(',')

    items = model.objects.filter(pk__in=keys)

    action = admin_model.get_action(action_code)

    if action is not None:
        function, *_ = action
        post = QueryDict('', mutable=True)
        length = len(items)
        for key, value in request.POST.items():
            post[key] = value
        post['post'] = True
        request.POST = post
        function(admin_model, request, items)
        return JsonResponse({'message': f'Action "{action_code}" was made on {length} {'items' if length > 1 else 'item'}.'})
    else:
        return JsonResponse({'message': 'Bad action name!'})

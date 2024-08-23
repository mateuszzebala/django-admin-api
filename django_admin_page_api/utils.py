import json
from django.http.multipartparser import MultiPartParser
from django.core.files.uploadhandler import TemporaryFileUploadHandler

def convert_comma_array(comma_array: str) -> list[str]:
    return [element.strip() for element in comma_array.split(',')]

def convert_query_object(query_string: str) -> dict[str, any]:
    try:
        data = json.loads(query_string)
        return data
    except:
        return {}

def parse_multipart_data(request):
    parser = MultiPartParser(
        META=request.META,
        input_data=request,
        upload_handlers=request.upload_handlers
    )
    return parser.parse()
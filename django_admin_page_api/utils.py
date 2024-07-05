import json

def convert_comma_array(comma_array: str) -> list[str]:
    return [element.strip() for element in comma_array.split(',')]

def convert_query_object(query_string: str) -> dict[str, any]:
    try:
        data = json.loads(query_string)
        return data
    except:
        return {}

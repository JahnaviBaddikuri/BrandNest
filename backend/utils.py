# utility functions

def validate_email(email):
    # check email format
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_positive_number(value):
    # check if positive
    try:
        number = float(value)
        return number > 0
    except (ValueError, TypeError):
        return False


def format_response(status, message=None, data=None, **kwargs):
    # format response
    response = {'status': status}
    if message:
        response['message'] = message
    if data:
        response['data'] = data
    response.update(kwargs)
    return response

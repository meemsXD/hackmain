from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response({'code': 'server_error', 'message': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    code = 'error'
    if response.status_code == 400:
        code = 'validation_error'
    elif response.status_code == 401:
        code = 'unauthorized'
    elif response.status_code == 403:
        code = 'forbidden'
    elif response.status_code == 404:
        code = 'not_found'
    return Response({'code': code, 'message': 'Ошибка запроса', 'details': response.data}, status=response.status_code)

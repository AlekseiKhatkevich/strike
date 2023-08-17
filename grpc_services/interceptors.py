from functools import partial

import grpc
import jwt

from internal.dependencies import user_id_context_var
from security.jwt import validate_jwt_token

__all__ = (
    'AuthInterceptor',
)


def abort(ignored_request, context, text):
    context.abort(grpc.StatusCode.UNAUTHENTICATED, text)


_abort_no_token = partial(abort, text='No JWT token present in request')
_abort_wrong_token = partial(abort, text='JWT token is not valid')

_abortion_no_token = grpc.unary_unary_rpc_method_handler(_abort_no_token)
_abortion_wrong_token = grpc.unary_unary_rpc_method_handler(_abort_wrong_token)


class AuthInterceptor(grpc.aio.ServerInterceptor):
    """
    Аутентифицирует запросы по переданному JWT токену.
    Пример Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOjM0fQ.UwT8lPNUcHRAEEGesEIBcYKItbrp04maOG03F22ec0Q
    """
    async def intercept_service(self, continuation, handler_call_details):
        for md in handler_call_details.invocation_metadata:
            if md.key == 'authorization':
                _, value = md.value.split(' ')
                try:
                    user_id = validate_jwt_token(value.strip())
                except jwt.PyJWTError:
                    return _abortion_wrong_token
                else:
                    user_id_context_var.set(user_id)
                    return await continuation(handler_call_details)
        else:
            return _abortion_no_token

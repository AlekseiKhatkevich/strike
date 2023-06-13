import builtins
import io
import pickle
from typing import Any


__all__ = (
    'restricted_loads',
)


safe_builtins = frozenset((
    'range',
    'complex',
    'set',
    'frozenset',
    'slice',
))

# https://stackoverflow.com/questions/25353753/python-can-i-safely-unpickle-untrusted-data
suspicious_modules = frozenset((
    'os',
    'subprocess',
    'builtins',
    'types',
    'typing',
    'functools',
))


class RestrictedUnpickler(pickle.Unpickler):
    """
    Не даем пиклу творить дичь.
    https://docs.python.org/3/library/pickle.html#restricting-globals
    """
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module in suspicious_modules:
            if name in safe_builtins:
                return getattr(builtins, name)
            else:
                # Forbid everything else.
                raise pickle.UnpicklingError(
                    f'global {module}.{name} is forbidden'
                )
        return super().find_class(module, name)


def restricted_loads(s: bytes) -> Any:
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()

from .user_auth_router import user_auth_router
from .appointment_router import appointment_router
from .report_router import report_router
from .admin_router import admin_router
from .health_router import health_router


__all__ = [
    'health_router',
    'user_auth_router',
    'appointment_router',
    'admin_router',
    'report_router',
]
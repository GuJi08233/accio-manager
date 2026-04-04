"""Accio 多账号管理面板。"""

from .web import app
from . import web_bulk_delete_extension as _web_bulk_delete_extension

__all__ = ["app"]

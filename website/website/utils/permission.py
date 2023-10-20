from typing import Type

from django.contrib.auth import get_permission_codename
from django.db.models import Model
from django.http import HttpRequest
from django.views import generic


def has_permission_for_view(view: generic.View, permission="view"):
    return has_permission(view.request, view.model, permission)  # type: ignore


def has_permission(request: HttpRequest, model: Type[Model], permission="view"):
    perm_name = model._meta.app_label + "." + get_permission_codename(permission, model._meta)
    return request.user.has_perm(perm_name)  # type: ignore

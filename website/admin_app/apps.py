from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "admin_app.admin.AdminSiteOTPRequired"


del AdminConfig

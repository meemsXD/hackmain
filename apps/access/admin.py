from django.contrib import admin
from .models import QRAccessToken, TokenAccessAttempt, DriverBatchAccessGrant
admin.site.register(QRAccessToken)
admin.site.register(TokenAccessAttempt)
admin.site.register(DriverBatchAccessGrant)

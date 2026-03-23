from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='audit_logs'
    )
    action = models.CharField(max_length=128, verbose_name='Действие')
    object_type = models.CharField(max_length=64, verbose_name='Тип объекта')
    object_id = models.CharField(max_length=64, verbose_name='ID объекта')
    before = models.JSONField(null=True, blank=True, verbose_name='До')
    after = models.JSONField(null=True, blank=True, verbose_name='После')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        db_table = 'audit_log'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.action} {self.object_type}:{self.object_id}'


def log(user, action, object_type, object_id, before=None, after=None):
    AuditLog.objects.create(
        user=user if getattr(user, 'pk', None) else None,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        before=before,
        after=after,
    )

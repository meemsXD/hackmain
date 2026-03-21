from .models import AuditEvent

def audit_log(actor_user, action, object_type, object_id, before_data=None, after_data=None, ip=None, user_agent=''):
    AuditEvent.objects.create(
        actor_user=actor_user if getattr(actor_user, 'pk', None) else None,
        actor_org=getattr(actor_user, 'organization', None) if getattr(actor_user, 'pk', None) else None,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        before_data=before_data,
        after_data=after_data,
        ip=ip,
        user_agent=user_agent or '',
    )

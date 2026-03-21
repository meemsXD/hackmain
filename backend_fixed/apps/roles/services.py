from django.utils import timezone
from .models import RoleRequest, UserRole
from apps.common.enums import RequestStatusChoices
from apps.audits.services import audit_log


def approve_role_request(role_request: RoleRequest, reviewer):
    role_request.status = RequestStatusChoices.APPROVED
    role_request.reviewed_by = reviewer
    role_request.reviewed_at = timezone.now()
    role_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])
    UserRole.objects.get_or_create(user=role_request.user, role=role_request.role, defaults={'granted_by': reviewer})
    audit_log(reviewer, 'role_request_approved', 'role_request', str(role_request.id), {'status': 'PENDING'}, {'status': 'APPROVED'})
    return role_request


def reject_role_request(role_request: RoleRequest, reviewer, reason: str):
    role_request.status = RequestStatusChoices.REJECTED
    role_request.reviewed_by = reviewer
    role_request.reviewed_at = timezone.now()
    role_request.rejection_reason = reason
    role_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'updated_at'])
    audit_log(reviewer, 'role_request_rejected', 'role_request', str(role_request.id), {'status': 'PENDING'}, {'status': 'REJECTED', 'reason': reason})
    return role_request

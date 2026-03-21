import secrets
import string
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from apps.audits.services import audit_log
from .models import QRAccessToken, TokenAccessAttempt, DriverBatchAccessGrant


def _manual_code(length=10):
    chars = string.ascii_uppercase + string.digits
    raw = ''.join(secrets.choice(chars) for _ in range(length))
    return f'{raw[:3]}-{raw[3:6]}-{raw[6:]}'


def ensure_batch_token(*, batch, created_by, expires_at):
    if expires_at > timezone.now() + timedelta(days=7):
        raise ValueError('Срок токена не может превышать 7 суток')
    raw = secrets.token_urlsafe(24)
    existing = QRAccessToken.objects.filter(batch=batch).first()
    if existing:
        existing.token_hash = make_password(raw)
        existing.expires_at = expires_at
        existing.created_by = created_by
        existing.save(update_fields=['token_hash', 'expires_at', 'created_by', 'updated_at'])
        existing.raw_token = raw
        return existing
    token = QRAccessToken.objects.create(
        batch=batch,
        token_hash=make_password(raw),
        manual_code=_manual_code(),
        expires_at=expires_at,
        created_by=created_by,
    )
    token.raw_token = raw
    return token


def extend_batch_token(*, batch, expires_at):
    token = batch.access_token
    if expires_at > token.issued_at + timedelta(days=7):
        raise ValueError('Продление не может выходить за пределы 7 суток от даты выпуска токена')
    token.expires_at = expires_at
    token.save(update_fields=['expires_at', 'updated_at'])
    return token


def log_access_attempt(*, batch=None, user=None, token_fragment='', manual_code='', success=False, failure_reason='', ip=None, user_agent=''):
    return TokenAccessAttempt.objects.create(
        batch=batch,
        user=user,
        token_fragment=token_fragment,
        manual_code=manual_code,
        success=success,
        failure_reason=failure_reason,
        ip=ip,
        user_agent=user_agent,
    )


def open_driver_access(*, user, raw_token=None, manual_code=None, ip=None, user_agent=''):
    if not user.user_roles.filter(role='DRIVER').exists():
        log_access_attempt(user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=False, failure_reason='forbidden_role', ip=ip, user_agent=user_agent)
        raise PermissionError('У пользователя нет роли водителя')

    token = None
    if manual_code:
        token = QRAccessToken.objects.select_related('batch').filter(manual_code=manual_code).first()
    elif raw_token:
        # raw_token is stored as token_hash; we embed a lookup-safe prefix in manual_code
        # so we must iterate, but only over non-expired tokens to limit the scan
        for candidate in QRAccessToken.objects.select_related('batch').filter(expires_at__gt=timezone.now()):
            if check_password(raw_token, candidate.token_hash):
                token = candidate
                break
    if not token:
        log_access_attempt(user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=False, failure_reason='invalid_token', ip=ip, user_agent=user_agent)
        raise ValueError('Токен не найден')
    batch = token.batch
    if token.expires_at <= timezone.now():
        log_access_attempt(batch=batch, user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=False, failure_reason='expired_token', ip=ip, user_agent=user_agent)
        raise ValueError('Срок действия токена истек')
    if batch.status not in ('CREATED', 'IN_TRANSIT'):
        log_access_attempt(batch=batch, user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=False, failure_reason='batch_closed', ip=ip, user_agent=user_agent)
        raise ValueError('Партия уже завершена или отменена')
    if user.organization_id != batch.processor_org_id:
        log_access_attempt(batch=batch, user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=False, failure_reason='forbidden_org', ip=ip, user_agent=user_agent)
        raise PermissionError('Организация водителя не совпадает с организацией-переработчиком')
    token.last_accessed_at = timezone.now()
    token.save(update_fields=['last_accessed_at'])
    DriverBatchAccessGrant.objects.update_or_create(batch=batch, driver=user, defaults={'expires_at': token.expires_at})
    log_access_attempt(batch=batch, user=user, token_fragment=(raw_token or '')[:8], manual_code=manual_code or '', success=True, ip=ip, user_agent=user_agent)
    audit_log(user, 'driver_access_opened', 'waste_batch', str(batch.id), None, {'batch_number': batch.batch_number})
    return batch

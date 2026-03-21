from django.db import transaction
from django.utils import timezone
from apps.common.enums import BatchStatusChoices
from apps.audits.services import audit_log
from apps.access.services import ensure_batch_token
from apps.chat.services import ensure_chat_thread, create_system_message
from .models import WasteBatch, BatchStatusHistory


def next_batch_number():
    from django.db import transaction
    prefix = timezone.now().strftime('WG-%Y%m%d-')
    with transaction.atomic():
        count = WasteBatch.objects.select_for_update().filter(batch_number__startswith=prefix).count() + 1
    return f'{prefix}{count:05d}'

@transaction.atomic
def create_batch(*, user, validated_data, signature_user=None):
    processor_org = validated_data['processor_org']
    delivery = getattr(getattr(processor_org, 'processor_profile', None), 'facility_address', processor_org.legal_address)
    batch = WasteBatch.objects.create(
        batch_number=next_batch_number(),
        creator_org=user.organization,
        created_by=user,
        delivery_address_snapshot=delivery,
        **validated_data,
    )
    BatchStatusHistory.objects.create(batch=batch, from_status='', to_status=BatchStatusChoices.CREATED, changed_by=user, signature_user=signature_user)
    token = ensure_batch_token(batch=batch, created_by=user, expires_at=validated_data['token_expires_at'])
    batch.raw_token = token.raw_token
    ensure_chat_thread(batch)
    audit_log(user, 'batch_created', 'waste_batch', str(batch.id), None, {'batch_number': batch.batch_number, 'status': batch.status})
    create_system_message(batch, f'Партия {batch.batch_number} создана')
    return batch

@transaction.atomic
def update_batch(*, batch, user, data):
    before = {
        'waste_type_id': str(batch.waste_type_id), 'quantity': str(batch.quantity), 'unit': batch.unit,
        'pickup_address': batch.pickup_address, 'processor_org_id': str(batch.processor_org_id), 'comment': batch.comment,
    }
    for key, value in data.items():
        setattr(batch, key, value)
    if 'processor_org' in data:
        batch.delivery_address_snapshot = getattr(getattr(batch.processor_org, 'processor_profile', None), 'facility_address', batch.processor_org.legal_address)
    batch.save()
    audit_log(user, 'batch_updated', 'waste_batch', str(batch.id), before, {'status': batch.status, 'pickup_address': batch.pickup_address, 'processor_org_id': str(batch.processor_org_id), 'comment': batch.comment})
    return batch

@transaction.atomic
def cancel_batch(*, batch, user, reason=''):
    if batch.status != BatchStatusChoices.CREATED:
        raise ValueError('Отмена возможна только для созданной партии')
    prev = batch.status
    batch.status = BatchStatusChoices.CANCELLED
    batch.cancelled_at = timezone.now()
    batch.save(update_fields=['status', 'cancelled_at', 'updated_at'])
    BatchStatusHistory.objects.create(batch=batch, from_status=prev, to_status=batch.status, changed_by=user, signature_user=user, reason=reason)
    create_system_message(batch, 'Партия отменена')
    audit_log(user, 'batch_cancelled', 'waste_batch', str(batch.id), {'status': prev}, {'status': batch.status})
    return batch

@transaction.atomic
def pickup_batch(*, batch, user):
    if batch.status != BatchStatusChoices.CREATED:
        raise ValueError('Забор возможен только из статуса CREATED')
    prev = batch.status
    batch.status = BatchStatusChoices.IN_TRANSIT
    batch.current_driver = user
    batch.picked_up_at = timezone.now()
    batch.save(update_fields=['status', 'current_driver', 'picked_up_at', 'updated_at'])
    BatchStatusHistory.objects.create(batch=batch, from_status=prev, to_status=batch.status, changed_by=user, signature_user=user)
    create_system_message(batch, f'Водитель {user.full_name} подтвердил забор партии')
    audit_log(user, 'batch_picked_up', 'waste_batch', str(batch.id), {'status': prev}, {'status': batch.status})
    return batch

@transaction.atomic
def mark_delivered(*, batch, user):
    if batch.status != BatchStatusChoices.IN_TRANSIT:
        raise ValueError('Доставка возможна только для партии в пути')
    if batch.delivered_at:
        raise ValueError('Доставка уже отмечена')
    batch.delivered_at = timezone.now()
    batch.save(update_fields=['delivered_at', 'updated_at'])
    create_system_message(batch, f'Водитель {user.full_name} отметил доставку партии')
    audit_log(user, 'batch_marked_delivered', 'waste_batch', str(batch.id), None, {'delivered_at': batch.delivered_at.isoformat()})
    return batch

@transaction.atomic
def accept_batch(*, batch, user):
    if batch.status != BatchStatusChoices.IN_TRANSIT:
        raise ValueError('Приемка возможна только для партии в пути')
    prev = batch.status
    batch.status = BatchStatusChoices.ACCEPTED
    batch.accepted_at = timezone.now()
    batch.save(update_fields=['status', 'accepted_at', 'updated_at'])
    BatchStatusHistory.objects.create(batch=batch, from_status=prev, to_status=batch.status, changed_by=user, signature_user=user)
    create_system_message(batch, f'Переработчик подтвердил приемку партии {batch.batch_number}')
    audit_log(user, 'batch_accepted', 'waste_batch', str(batch.id), {'status': prev}, {'status': batch.status})
    return batch

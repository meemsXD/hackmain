import csv
from io import StringIO, BytesIO
from django.http import HttpResponse
from openpyxl import Workbook
from apps.batches.models import WasteBatch


def apply_batch_filters(qs, params):
    if params.get('status'):
        qs = qs.filter(status=params['status'])
    if params.get('batch_number'):
        qs = qs.filter(batch_number__icontains=params['batch_number'])
    if params.get('creator_org'):
        qs = qs.filter(creator_org_id=params['creator_org'])
    if params.get('processor_org'):
        qs = qs.filter(processor_org_id=params['processor_org'])
    if params.get('waste_type'):
        qs = qs.filter(waste_type_id=params['waste_type'])
    if params.get('date_from'):
        qs = qs.filter(created_at__date__gte=params['date_from'])
    if params.get('date_to'):
        qs = qs.filter(created_at__date__lte=params['date_to'])
    if params.get('has_blocked_attempts') == 'true':
        qs = qs.filter(access_attempts__success=False).distinct()
    return qs


def export_batches_csv(qs):
    buffer = StringIO()
    buffer.write('\ufeff')  # BOM for Excel UTF-8 compatibility
    writer = csv.writer(buffer)
    writer.writerow(['Номер партии', 'Тип отходов', 'Количество', 'Ед.', 'Статус', 'Образователь', 'Переработчик', 'Адрес вывоза', 'Адрес доставки', 'Создана', 'Забрана', 'Доставлена', 'Принята', 'Срок токена'])
    for b in qs.select_related('waste_type', 'creator_org', 'processor_org', 'access_token'):
        writer.writerow([
            b.batch_number, b.waste_type.name, b.quantity, b.unit, b.status, b.creator_org.name, b.processor_org.name,
            b.pickup_address, b.delivery_address_snapshot, b.created_at,
            b.picked_up_at or '', b.delivered_at or '', b.accepted_at or '',
            getattr(getattr(b, 'access_token', None), 'expires_at', '') or ''
        ])
    resp = HttpResponse(buffer.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8-sig')
    resp['Content-Disposition'] = 'attachment; filename="journal.csv"'
    return resp


def export_batches_xlsx(qs):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Journal'
    ws.append(['Номер партии', 'Тип отходов', 'Количество', 'Ед.', 'Статус', 'Образователь', 'Переработчик', 'Адрес вывоза', 'Адрес доставки', 'Создана', 'Забрана', 'Доставлена', 'Принята', 'Срок токена'])
    for b in qs.select_related('waste_type', 'creator_org', 'processor_org', 'access_token'):
        token_expires = getattr(getattr(b, 'access_token', None), 'expires_at', None)
        ws.append([
            b.batch_number, b.waste_type.name, float(b.quantity), b.unit, b.status, b.creator_org.name, b.processor_org.name,
            b.pickup_address, b.delivery_address_snapshot,
            b.created_at.replace(tzinfo=None) if b.created_at else None,
            b.picked_up_at.replace(tzinfo=None) if b.picked_up_at else None,
            b.delivered_at.replace(tzinfo=None) if b.delivered_at else None,
            b.accepted_at.replace(tzinfo=None) if b.accepted_at else None,
            token_expires.replace(tzinfo=None) if token_expires else None,
        ])
    content = BytesIO()
    wb.save(content)
    resp = HttpResponse(content.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="journal.xlsx"'
    return resp

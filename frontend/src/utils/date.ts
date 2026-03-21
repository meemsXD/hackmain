import { format, isValid, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return '—';
  }
  const parsed = parseISO(value);
  if (!isValid(parsed)) {
    return value;
  }
  return format(parsed, 'dd.MM.yyyy HH:mm', { locale: ru });
}

export function formatDate(value?: string | null): string {
  if (!value) {
    return '—';
  }
  const parsed = parseISO(value);
  if (!isValid(parsed)) {
    return value;
  }
  return format(parsed, 'dd.MM.yyyy', { locale: ru });
}

export function isExpired(value?: string | null): boolean {
  if (!value) {
    return false;
  }
  const parsed = parseISO(value);
  if (!isValid(parsed)) {
    return false;
  }
  return parsed.getTime() < Date.now();
}

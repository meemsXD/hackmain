import QRCode from 'react-qr-code';
import type { BatchQr } from '@/api/types';
import { Badge } from '@/components/ui/Badge';
import { formatDateTime, isExpired } from '@/utils/date';

type QrCodeCardProps = {
  qr: BatchQr | null;
};

export function QrCodeCard({ qr }: QrCodeCardProps) {
  if (!qr) {
    return (
      <div className="surface p-4">
        <p className="text-sm text-brand-700">QR-код для этой партии пока не создан.</p>
      </div>
    );
  }

  const expired = isExpired(qr.time) || !qr.is_active;

  return (
    <div className="surface p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-700">QR доступ водителя</h3>
      <div className="grid gap-4 md:grid-cols-[140px_1fr]">
        <div className="grid place-items-center rounded-xl bg-brand-50 p-3">
          <QRCode value={qr.code} size={110} />
        </div>
        <div className="space-y-2 text-sm text-brand-800">
          <p>
            <span className="font-semibold">Код доступа:</span> {qr.code}
          </p>
          <p>
            <span className="font-semibold">Срок действия:</span> {formatDateTime(qr.time)}
          </p>
          <Badge tone={expired ? 'danger' : 'success'}>{expired ? 'Истек' : 'Активен'}</Badge>
        </div>
      </div>
    </div>
  );
}

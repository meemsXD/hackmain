import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  open,
  title,
  description,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onCancel}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button variant="danger" loading={loading} onClick={onConfirm}>
            {confirmText}
          </Button>
        </div>
      }
    >
      <p className="text-sm text-brand-800">{description}</p>
    </Modal>
  );
}

import { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

type SignatureConfirmModalProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  onConfirm: (token: string) => Promise<void> | void;
};

export function SignatureConfirmModal({ open, title, onClose, onConfirm }: SignatureConfirmModalProps) {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!token.trim()) {
      setError('Введите токен подписи.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await onConfirm(token.trim());
      setToken('');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      title={title}
      onClose={onClose}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>
            Отмена
          </Button>
          <Button loading={loading} onClick={handleSubmit}>
            Подтвердить
          </Button>
        </div>
      }
    >
      <Input
        label="Токен подписи"
        type="password"
        value={token}
        onChange={(event) => setToken(event.target.value)}
        error={error}
        hint="Токен хранится локально в вашем профиле и нужен для критичных действий."
      />
    </Modal>
  );
}

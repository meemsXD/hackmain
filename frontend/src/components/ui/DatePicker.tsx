import { Input } from '@/components/ui/Input';

type DatePickerProps = {
  label?: string;
  value?: string;
  onChange: (value: string) => void;
  error?: string;
};

export function DatePicker({ label, value, onChange, error }: DatePickerProps) {
  return (
    <Input
      label={label}
      type="datetime-local"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      error={error}
    />
  );
}

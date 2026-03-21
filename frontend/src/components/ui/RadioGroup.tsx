type RadioOption = {
  value: string;
  label: string;
};

type RadioGroupProps = {
  label?: string;
  name: string;
  value: string;
  options: RadioOption[];
  onChange: (value: string) => void;
};

export function RadioGroup({ label, name, value, options, onChange }: RadioGroupProps) {
  return (
    <div className="space-y-2">
      {label ? <p className="text-sm font-medium text-brand-900">{label}</p> : null}
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <label
            key={option.value}
            className={`inline-flex cursor-pointer items-center gap-2 rounded-full border px-3 py-1.5 text-sm transition ${
              value === option.value ? 'border-brand-500 bg-brand-50 text-brand-900' : 'border-brand-200 text-brand-700'
            }`}
          >
            <input
              type="radio"
              className="hidden"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
            />
            {option.label}
          </label>
        ))}
      </div>
    </div>
  );
}

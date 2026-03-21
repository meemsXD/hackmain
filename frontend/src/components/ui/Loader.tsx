type LoaderProps = {
  label?: string;
};

export function Loader({ label = 'Загрузка...' }: LoaderProps) {
  return (
    <div className="inline-flex items-center gap-2 text-sm text-brand-700">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      {label}
    </div>
  );
}

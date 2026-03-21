type TabItem = {
  value: string;
  label: string;
};

type TabsProps = {
  tabs: TabItem[];
  value: string;
  onChange: (value: string) => void;
};

export function Tabs({ tabs, value, onChange }: TabsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {tabs.map((tab) => {
        const active = tab.value === value;
        return (
          <button
            key={tab.value}
            type="button"
            onClick={() => onChange(tab.value)}
            className={`rounded-full border px-3 py-1.5 text-sm transition ${
              active ? 'border-brand-500 bg-brand-100 text-brand-900' : 'border-brand-200 bg-white text-brand-700 hover:bg-brand-50'
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}

import type { ReactNode } from 'react';

type Column<T> = {
  key: string;
  title: string;
  render: (row: T) => ReactNode;
  className?: string;
};

type TableProps<T> = {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T) => string | number;
};

export function Table<T>({ columns, data, rowKey }: TableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-brand-100">
      <table className="w-full min-w-[760px] border-collapse bg-white text-left text-sm">
        <thead className="bg-brand-50 text-brand-800">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={`px-3 py-2 font-semibold ${column.className ?? ''}`}>
                {column.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={rowKey(row)} className="border-t border-brand-100 text-brand-900">
              {columns.map((column) => (
                <td key={column.key} className={`px-3 py-2 align-top ${column.className ?? ''}`}>
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

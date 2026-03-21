import type { Organization } from '@/api/types';

type OrganizationSummaryCardProps = {
  organization: Organization | null;
};

export function OrganizationSummaryCard({ organization }: OrganizationSummaryCardProps) {
  return (
    <div className="surface p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-700">Организация</h3>
      {!organization ? (
        <p className="text-sm text-brand-700">Организация не привязана.</p>
      ) : (
        <div className="grid gap-2 text-sm text-brand-900">
          <p>
            <span className="font-semibold">Название:</span> {organization.name}
          </p>
          <p>
            <span className="font-semibold">ИНН:</span> {organization.inn}
          </p>
          <p>
            <span className="font-semibold">КПП:</span> {organization.kpp}
          </p>
        </div>
      )}
    </div>
  );
}

import { useTranslation } from 'react-i18next';

export interface HeatmapRow {
  name: string;
  total: number;
  covered: number;
  pct: number;
}

interface HeatmapTableProps {
  data: HeatmapRow[];
  title: string;
}

function getCoverageColor(pct: number): string {
  if (pct >= 75) return 'bg-green-50 text-green-700';
  if (pct >= 50) return 'bg-amber-50 text-amber-700';
  return 'bg-error-container/30 text-error';
}

export function HeatmapTable({ data, title }: HeatmapTableProps) {
  const { t } = useTranslation();

  if (data.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {title}
        </h3>
        <p className="font-sans text-sm text-on-surface-variant">
          {t('common.no_data')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-6 pt-5 pb-3">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          {title}
        </h3>
      </div>
      <table className="w-full">
        <thead>
          <tr className="bg-surface-container-low/50">
            <th className="text-left px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              {t('hr.col_name', 'Nom')}
            </th>
            <th className="text-right px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              {t('hr.col_total', 'Total')}
            </th>
            <th className="text-right px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              {t('hr.col_covered', 'Couverts')}
            </th>
            <th className="text-right px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
              {t('hr.col_coverage', 'Couverture')}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/10">
          {data.map((row) => (
            <tr key={row.name} className="hover:bg-surface-bright">
              <td className="px-6 py-3 text-sm font-sans text-on-surface">
                {row.name}
              </td>
              <td className="px-6 py-3 text-sm font-sans text-on-surface-variant text-right">
                {row.total}
              </td>
              <td className="px-6 py-3 text-sm font-sans text-on-surface-variant text-right">
                {row.covered}
              </td>
              <td className="px-6 py-3 text-right">
                <span
                  className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${getCoverageColor(row.pct)}`}
                  data-testid="coverage-badge"
                >
                  {row.pct.toFixed(1)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

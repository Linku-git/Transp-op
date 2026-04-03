import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEmployeeStore } from '@/stores/employeeStore';
import { EmployeeForm } from './EmployeeForm';
import { extractApiError } from '@/lib/apiError';
import type { EmployeeCreate } from '@/types/employee';

export function EmployeeCreatePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { createEmployee } = useEmployeeStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (data: EmployeeCreate) => {
      setIsSubmitting(true);
      setApiError(null);
      try {
        await createEmployee(data);
        navigate('/employees');
      } catch (err: unknown) {
        setApiError(extractApiError(err, t('common.error')));
      } finally {
        setIsSubmitting(false);
      }
    },
    [createEmployee, navigate, t],
  );

  const handleCancel = useCallback(() => {
    navigate('/employees');
  }, [navigate]);

  return (
    <div>
      <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight mb-8">
        {t('employees.create_title', 'Nouvel employe')}
      </h1>

      <EmployeeForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  );
}

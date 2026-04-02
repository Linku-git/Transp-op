import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEmployeeStore } from '@/stores/employeeStore';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmployeeForm } from './EmployeeForm';
import type { EmployeeCreate } from '@/types/employee';
import type { AxiosError } from 'axios';
import type { ApiError } from '@/types';

export function EmployeeEditPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { currentEmployee, isLoading, error, fetchEmployee, updateEmployee } =
    useEmployeeStore();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchEmployee(id);
    }
  }, [id, fetchEmployee]);

  const handleSubmit = useCallback(
    async (data: EmployeeCreate) => {
      if (!id) return;
      setIsSubmitting(true);
      setApiError(null);
      try {
        await updateEmployee(id, data);
        navigate('/employees');
      } catch (err: unknown) {
        const axiosErr = err as AxiosError<ApiError>;
        setApiError(
          axiosErr.response?.data?.detail ?? t('common.error'),
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [id, updateEmployee, navigate, t],
  );

  const handleCancel = useCallback(() => {
    navigate('/employees');
  }, [navigate]);

  /* Loading state */
  if (isLoading && !currentEmployee) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <Skeleton variant="rectangular" className="w-full" height="400px" />
      </div>
    );
  }

  /* Not found / error state */
  if (!isLoading && !currentEmployee) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2">
        <p className="font-sans text-xl font-semibold text-on-surface">
          {error ?? t('employees.not_found', 'Employe introuvable')}
        </p>
        <button
          onClick={() => navigate('/employees')}
          className="text-sm text-primary font-sans hover:underline"
        >
          {t('employees.back_to_list', 'Retour a la liste')}
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight mb-8">
        {t('employees.edit_title', "Modifier l'employe")}:{' '}
        {currentEmployee?.first_name} {currentEmployee?.last_name}
      </h1>

      {currentEmployee && (
        <EmployeeForm
          initialData={currentEmployee}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
          apiError={apiError}
          isEditMode
        />
      )}
    </div>
  );
}

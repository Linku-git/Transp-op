import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVehicle } from '@/api/vehicles';
import type { Vehicle } from '@/types/vehicle';
import { VehicleForm } from './VehicleForm';

export function VehicleEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getVehicle(id)
      .then(setVehicle)
      .catch(() => navigate('/vehicles'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40 text-on-surface-variant text-sm">
        Chargement…
      </div>
    );
  }

  if (!vehicle) return null;

  return <VehicleForm vehicle={vehicle} />;
}

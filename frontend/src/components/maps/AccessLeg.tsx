import { Polyline } from '@vis.gl/react-google-maps';

interface AccessLegProps {
  employeeLat: number;
  employeeLng: number;
  zoneLat: number;
  zoneLng: number;
}

export function AccessLeg({
  employeeLat,
  employeeLng,
  zoneLat,
  zoneLng,
}: AccessLegProps) {
  return (
    <Polyline
      path={[
        { lat: employeeLat, lng: employeeLng },
        { lat: zoneLat, lng: zoneLng },
      ]}
      strokeColor="#495e8a"
      strokeWeight={1.5}
      strokeOpacity={0.45}
    />
  );
}

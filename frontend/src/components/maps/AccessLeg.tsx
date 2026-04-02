import { Polyline } from 'react-leaflet';

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
      positions={[
        [employeeLat, employeeLng],
        [zoneLat, zoneLng],
      ]}
      pathOptions={{
        color: '#495e8a',
        weight: 1.5,
        opacity: 0.5,
        dashArray: '4 8',
      }}
    />
  );
}

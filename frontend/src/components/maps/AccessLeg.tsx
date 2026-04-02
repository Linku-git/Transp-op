import { Polyline } from '@react-google-maps/api';

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
      options={{
        strokeColor: '#495e8a',
        strokeWeight: 1.5,
        strokeOpacity: 0.5,
        icons: [
          {
            icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 4 },
            offset: '0',
            repeat: '20px',
          },
        ],
      }}
    />
  );
}

import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

const DataMap = ({ data }) => {
  // Find a central point for the map view
  const centerLat = data.reduce((acc, curr) => acc + curr.latitude, 0) / data.length;
  const centerLon = data.reduce((acc, curr) => acc + curr.longitude, 0) / data.length;

  return (
    <div className="mt-4">
        <h3 className="text-lg font-semibold mb-2 text-cyan-400">Map of Data Points</h3>
        <div className="h-96 w-full rounded-lg overflow-hidden border-2 border-slate-600">
            <MapContainer center={[centerLat, centerLon]} zoom={3} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {data.map((point, index) => (
                    <Marker key={index} position={[point.latitude, point.longitude]}>
                        <Popup>
                            Float: {point.platform_number || 'N/A'}<br />
                            Temp: {point.temperature?.toFixed(2) || 'N/A'} °C<br />
                            Lat: {point.latitude.toFixed(3)}, Lon: {point.longitude.toFixed(3)}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    </div>
  );
};

export default DataMap;
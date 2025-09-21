import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ProfileChart = ({ data }) => {
  const chartData = data.sort((a, b) => a.pressure - b.pressure);
  const hasTemp = 'temperature' in data[0];
  const hasSalinity = 'salinity' in data[0];
  const floatId = data[0].platform_number;

  return (
    <div className="mt-4">
        <h3 className="text-lg font-semibold mb-2 text-cyan-400">Profile for Float #{floatId}</h3>
        <div className="h-96 w-full bg-slate-800 p-4 rounded-lg border-2 border-slate-600">
            <ResponsiveContainer>
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <YAxis dataKey="pressure" type="number" domain={['dataMax', 'dataMin']} reversed={true} stroke="#94a3b8" label={{ value: 'Pressure (dbar)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
                    <XAxis type="number" dataKey={hasTemp ? "temperature" : "salinity"} stroke="#94a3b8" label={{ value: hasTemp ? 'Temperature (°C)' : 'Salinity (PSU)', position: 'insideBottom', offset: -5, fill: '#94a3b8' }} domain={['dataMin - 1', 'dataMax + 1']} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Legend />
                    {hasTemp && <Line type="monotone" dataKey="temperature" stroke="#22d3ee" strokeWidth={2} dot={false} />}
                    {hasSalinity && <Line type="monotone" dataKey="salinity" stroke="#a78bfa" strokeWidth={2} dot={false} />}
                </LineChart>
            </ResponsiveContainer>
        </div>
    </div>
  );
};

export default ProfileChart;
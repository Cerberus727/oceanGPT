import React from 'react';

const DataTable = ({ data }) => {
  if (!data || data.length === 0) return null;
  const headers = Object.keys(data[0]);
  
  return (
    <div className="mt-4 overflow-x-auto border border-slate-600 rounded-lg">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-800">
          <tr>
            {headers.map(header => (
              <th key={header} className="p-2 font-semibold capitalize">{header.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="bg-slate-700 border-t border-slate-600 hover:bg-slate-600/50">
              {headers.map(header => (
                <td key={header} className="p-2">{String(row[header])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
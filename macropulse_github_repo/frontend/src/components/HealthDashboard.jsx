import React, { useEffect, useState } from 'react';
import API from '../api';

function statusColor(days, freq){
  if(days == null) return 'gray';
  if(freq === 'D') return days <= 2 ? 'green' : days <= 7 ? 'orange' : 'red';
  if(freq === 'W') return days <= 14 ? 'green' : days <= 30 ? 'orange' : 'red';
  if(freq === 'M') return days <= 45 ? 'green' : days <= 75 ? 'orange' : 'red';
  if(freq === 'Q') return days <= 120 ? 'green' : days <= 200 ? 'orange' : 'red';
  return days <= 30 ? 'green' : 'orange';
}

export default function HealthDashboard(){
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async ()=>{
    try{
      const res = await API.get('/data/health/data');
      setRows(res.data.indicators || []);
      setError('');
    }catch{
      setError('Failed to load health data');
    }finally{
      setLoading(false);
    }
  };

  useEffect(()=>{ load(); const id=setInterval(load, 60000); return ()=>clearInterval(id); },[]);

  return (
    <div>
      <h2>Data Health & Freshness</h2>
      {loading ? <p>Loading...</p> : error ? <p style={{color:'red'}}>{error}</p> :
        <table border="1" cellPadding="6" style={{borderCollapse:'collapse', width:'100%'}}>
          <thead><tr><th>Code</th><th>Name</th><th>Source</th><th>Freq</th><th>Last Obs Date</th><th>Last Obs Value</th><th>Staleness (days)</th><th>Status</th></tr></thead>
          <tbody>
            {rows.map((r,idx)=>{
              const color = statusColor(r.staleness_days, r.frequency);
              return (
                <tr key={idx}>
                  <td>{r.code}</td><td>{r.name}</td><td>{r.source}</td><td>{r.frequency}</td>
                  <td>{r.last_obs_date || '-'}</td><td>{r.last_obs_value ?? '-'}</td>
                  <td style={{textAlign:'right'}}>{r.staleness_days ?? '-'}</td>
                  <td style={{color}}>{color.toUpperCase()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>}
    </div>
  );
}

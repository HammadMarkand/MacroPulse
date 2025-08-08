import React, { useEffect, useState } from 'react';
import API from '../api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, TimeScale);

export default function SeriesChart({ code='FEDFUNDS' }){
  const [series, setSeries] = useState([]);
  const [meta, setMeta] = useState({ code, name: code, unit: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    const load = async ()=>{
      try{
        const res = await API.get(`/data/series/${code}`);
        setSeries(res.data.observations || []);
        setMeta(res.data.indicator || { code, name: code, unit: '' });
        setError('');
      }catch{
        setError('Failed to load series');
      }finally{ setLoading(false); }
    };
    load();
  },[code]);

  if(loading) return <p>Loading {code}...</p>;
  if(error) return <p style={{color:'red'}}>{error}</p>;

  const data = {
    labels: series.map(p => new Date(p.date)),
    datasets: [{ label: `${meta.name} (${meta.unit})`, data: series.map(p => p.value), tension: 0.2 }]
  };
  const options = { responsive: true, scales: { x: { type: 'time', time: { unit: 'month' }}, y: { beginAtZero: false }}};

  return (<div style={{marginBottom: 24}}><h3>{meta.name} — {meta.code}</h3><Line data={data} options={options} /></div>);
}

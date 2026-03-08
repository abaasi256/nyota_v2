import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Cpu, Network, Database } from 'lucide-react';

const initialData = [
  { name: '00:00', requests: 400, events: 240 },
  { name: '04:00', requests: 300, events: 139 },
  { name: '08:00', requests: 200, events: 980 },
  { name: '12:00', requests: 278, events: 390 },
  { name: '16:00', requests: 189, events: 480 },
  { name: '20:00', requests: 239, events: 380 },
  { name: '24:00', requests: 349, events: 430 },
];

export default function Dashboard() {
  const [graphData, setGraphData] = useState(initialData);
  const [msgCount, setMsgCount] = useState(1409);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/events");
    
    ws.onopen = () => console.log("Connected to Nyota Event Bus Stream.");
    
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        console.log("Nyota OS Event:", payload.subject, payload.data);
        
        // Bump messages visually
        setMsgCount(prev => prev + 1);

        // Append to timeline chart magically
        setGraphData(prev => {
          const arr = [...prev];
          arr[arr.length - 1] = {
             ...arr[arr.length - 1],
             events: arr[arr.length - 1].events + 2,
             requests: arr[arr.length - 1].requests + 1
          };
          return arr;
        });
      } catch (err) {
        console.error("WS Parse error", err);
      }
    };
    
    return () => ws.close();
  }, []);

  return (
    <div className="dashboard-content">
      <div className="metric-grid">
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">JetStream Throughput</span>
            <Activity size={16} />
          </div>
          <div className="metric-value">{msgCount.toLocaleString()} <span style={{fontSize: 14, color: 'var(--text-muted)'}}>msg/s</span></div>
          <div className="metric-trend trend-up">↑ +14.2% vs yesterday</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Active AI Agents</span>
            <Cpu size={16} />
          </div>
          <div className="metric-value">4 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Nodes</span></div>
          <div className="metric-trend trend-up">Zuri, Amani, Nia, Baraka</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">NATS Hub Connections</span>
            <Network size={16} />
          </div>
          <div className="metric-value">9 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Socket Pairs</span></div>
          <div className="metric-trend trend-up">0 Dropped Packet Loss</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Core Postgres Memory</span>
            <Database size={16} />
          </div>
          <div className="metric-value">14.2 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>GB</span></div>
          <div className="metric-trend trend-down">Stable WAL Allocation</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="panel glass-panel">
          <h2 className="panel-title"><Activity size={20} /> Event Bus Flow (24h)</h2>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={graphData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorEvt" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.2)" fontSize={12} tickMargin={10} />
                <YAxis stroke="rgba(255,255,255,0.2)" fontSize={12} tickMargin={10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(9, 9, 11, 0.9)', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="requests" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorReq)" />
                <Area type="monotone" dataKey="events" stroke="#10b981" fillOpacity={1} fill="url(#colorEvt)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel glass-panel">
          <h2 className="panel-title">Active Operating Systems</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>System</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Nyota Core</td>
                <td><span className="status-badge status-active">Online</span></td>
              </tr>
              <tr>
                <td>Growth OS</td>
                <td><span className="status-badge status-active">Online</span></td>
              </tr>
              <tr>
                <td>Revenue OS</td>
                <td><span className="status-badge status-active">Online</span></td>
              </tr>
              <tr>
                <td>Security OS</td>
                <td><span className="status-badge status-active">Online</span></td>
              </tr>
              <tr>
                <td>Temporal Workflow</td>
                <td><span className="status-badge status-active">Polling</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

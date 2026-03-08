import { useState, useEffect } from 'react';
import { MessageCircle, DollarSign, Package, RefreshCw } from 'lucide-react';

interface RevenueLead {
  phone_number: string;
  intent_score: number;
  status: string;
  last_interaction: string;
}

export default function RevenueOS() {
  const [leads, setLeads] = useState<RevenueLead[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/revenue/leads');
      const data = await response.json();
      setLeads(data);
    } catch (err) {
      console.error('Failed to fetch revenue leads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div className="metric-grid">
        <div className="metric-card glass-panel" style={{borderTop: '2px solid var(--success)'}}>
          <div className="metric-header">
            <span className="metric-title">Active AI Sales (Nia)</span>
            <MessageCircle size={16} />
          </div>
          <div className="metric-value">{leads.length} <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Engaged Customers</span></div>
          <div className="metric-trend trend-up">Avg Response: 1.4s</div>
        </div>
        
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Pipeline Value (Est)</span>
            <DollarSign size={16} />
          </div>
          <div className="metric-value">$8.2k</div>
          <div className="metric-trend trend-up">↑ +$1.2k today</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">GPU Inventory Tracker</span>
            <Package size={16} />
          </div>
          <div className="metric-value">46 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Units</span></div>
          <div className="metric-trend trend-down">RTX 4090: LOW STOCK (3)</div>
        </div>
      </div>

      <div className="panel glass-panel">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
          <h2 className="panel-title" style={{margin: 0}}>Recent WhatsApp CRM Events</h2>
          <button className="action-btn" onClick={fetchLeads} style={{borderRadius: 8, height: 36, width: 36}}>
            <RefreshCw size={16} className={loading ? "spin" : ""} />
          </button>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Lead Phone</th>
              <th>Intent Score</th>
              <th>Last Interaction Date</th>
              <th>Nia Pipeline Status</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, idx) => (
              <tr key={idx}>
                <td className="text-mono" style={{color: 'var(--text-primary)'}}>{lead.phone_number}</td>
                <td>
                  <div style={{
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 8, 
                    color: lead.intent_score > 70 ? 'var(--success)' : 'var(--warning)'
                  }}>
                    {lead.intent_score}% 
                    <div style={{width: 60, height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2}}>
                      <div style={{width: `${lead.intent_score}%`, height: '100%', background: 'currentColor', borderRadius: 2}}></div>
                    </div>
                  </div>
                </td>
                <td style={{color: 'var(--text-muted)'}}>{new Date(lead.last_interaction).toLocaleString()}</td>
                <td>
                  <span className={`status-badge ${
                    lead.status === 'WON' ? 'status-active' : 
                    lead.status === 'LOST' ? 'status-error' : 'status-pending'
                  }`}>
                    {lead.status}
                  </span>
                </td>
              </tr>
            ))}
            {leads.length === 0 && !loading && (
              <tr>
                <td colSpan={4} style={{textAlign: 'center', padding: '32px', color: 'var(--text-muted)'}}>No CRM leads captured yet. Awaiting WhatsApp Message.</td>
              </tr>
            )}
            {loading && leads.length === 0 && (
              <tr>
                <td colSpan={4} style={{textAlign: 'center', padding: '32px', color: 'var(--text-muted)'}}>Connecting to Revenue DB...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
}

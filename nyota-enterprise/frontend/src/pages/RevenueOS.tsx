
import { MessageCircle, DollarSign, Package } from 'lucide-react';

export default function RevenueOS() {
  return (
    <div>
      <div className="metric-grid">
        <div className="metric-card glass-panel" style={{borderTop: '2px solid var(--success)'}}>
          <div className="metric-header">
            <span className="metric-title">Active AI Sales (Nia)</span>
            <MessageCircle size={16} />
          </div>
          <div className="metric-value">2 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Chats</span></div>
          <div className="metric-trend trend-up">Avg Response: 1.4s</div>
        </div>
        
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Pipeline Value</span>
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
        <h2 className="panel-title" style={{marginBottom: 20}}>Recent WhatsApp CRM Events</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Lead Phone</th>
              <th>Message Intent</th>
              <th>Nia Response</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>+256 701 111 111</td>
              <td>Price inquiry (RTX 3060)</td>
              <td>Routed to fallback Kimi LLM</td>
              <td><span className="status-badge status-active">Closed (Won)</span></td>
            </tr>
            <tr>
              <td>+256 700 000 000</td>
              <td>Stock check (RTX 4090)</td>
              <td>Quoted $2,100 from database</td>
              <td><span className="status-badge status-pending">Negotiation</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

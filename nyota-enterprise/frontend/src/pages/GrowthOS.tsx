
import { Search, PenTool, Link, PlusCircle } from 'lucide-react';

export default function GrowthOS() {
  return (
    <div>
      <div className="metric-grid">
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Zuri Crawler Status</span>
            <Search size={16} />
          </div>
          <div className="metric-value">Idle <span style={{fontSize: 14, color: 'var(--success)'}}>Ready</span></div>
          <div className="metric-trend">0 Active Jobs</div>
        </div>
        
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Amani Drafter Stats</span>
            <PenTool size={16} />
          </div>
          <div className="metric-value">12 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Drafts / wk</span></div>
          <div className="metric-trend trend-up">Last draft size: 928 wds</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Avg Link Strength</span>
            <Link size={16} />
          </div>
          <div className="metric-value">DR 48</div>
          <div className="metric-trend trend-up">↑ +2 this month</div>
        </div>
      </div>

      <div className="panel glass-panel" style={{marginBottom: 24}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
          <h2 className="panel-title" style={{margin: 0}}>Latest Content Generation Workflows</h2>
          <button className="action-btn" style={{width: 'auto', padding: '0 16px', borderRadius: '8px', background: 'var(--accent-primary)', color: '#fff', border: 'none'}}>
            <PlusCircle size={16} style={{marginRight: 8}}/> Trigger Manual Crawl
          </button>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Temporal ID</th>
              <th>Target Keyword</th>
              <th>Crawl Size</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="text-mono">content-gen-ai-automated-saas</td>
              <td>ai automated saas deployment</td>
              <td>82.8 KB</td>
              <td><span className="status-badge status-pending">Human Approval Gate</span></td>
            </tr>
            <tr>
              <td className="text-mono">content-gen-enterprise-grade</td>
              <td>enterprise grade networking</td>
              <td>56.3 KB</td>
              <td><span className="status-badge status-active">Completed</span></td>
            </tr>
            <tr>
              <td className="text-mono">content-gen-rtx-4090</td>
              <td>buy rtx 4090 in kampala</td>
              <td>56.3 KB</td>
              <td><span className="status-badge status-active">Completed</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

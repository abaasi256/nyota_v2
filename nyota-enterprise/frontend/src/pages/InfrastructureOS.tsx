import { Database, ShieldAlert, Cpu, TerminalSquare, Network } from 'lucide-react';

export default function InfrastructureOS() {
  return (
    <div>
      <div className="metric-grid">
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Security OS Audits</span>
            <ShieldAlert size={16} />
          </div>
          <div className="metric-value">841</div>
          <div className="metric-trend trend-down">0 Quarantine events today</div>
        </div>
        
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Temporal Workflows</span>
            <Cpu size={16} />
          </div>
          <div className="metric-value">3 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Active</span></div>
          <div className="metric-trend">2 pending syncs</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">DB Disk Usage</span>
            <Database size={16} />
          </div>
          <div className="metric-value">4.2 <span style={{fontSize: 14, color: 'var(--text-muted)'}}>GB</span></div>
          <div className="metric-trend trend-down">20GB Max Provisioned</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="panel glass-panel">
          <h2 className="panel-title"><TerminalSquare size={20} /> System Audit Logs</h2>
          <div style={{background: '#000', padding: 16, borderRadius: 8, fontFamily: 'monospace', fontSize: 13, color: '#A1A1AA', height: 250, overflowY: 'auto'}}>
            <div style={{color: '#10B981'}}>[09:27:49] SECURITY_OS: Evaluated & passed payload matching events.growth.*</div>
            <div>[09:34:51] SYSTEM: Temporal Workflow `content-gen-enterprise` signaled Amani completion</div>
            <div>[09:35:19] NATS: Growth Crawler agent connected to port 4222</div>
            <div style={{color: '#F59E0B'}}>[10:45:22] ORCH: Temporal worker scaling to queue `growth-task-queue`</div>
            <div style={{color: '#EF4444'}}>[10:47:09] SYSTEM: SQL connection timeout in Drafter. Retrying.</div>
            <div>[10:50:32] NATS: New heartbeat from Revenue Agent Nia</div>
          </div>
        </div>
        
        <div className="panel glass-panel">
          <h2 className="panel-title" style={{marginBottom: 10}}>External Dashboards</h2>
          <p style={{fontSize: 14, color: 'var(--text-secondary)', marginBottom: 20}}>
            Gain direct administrative access into the underlying open source orchestration clusters powering Nyota.
          </p>
          
          <div style={{display: 'flex', flexDirection: 'column', gap: 12}}>
            <a href="http://localhost:8080" target="_blank" className="action-btn" style={{width: '100%', height: 'auto', padding: '12px 16px', borderRadius: '8px', justifyContent: 'flex-start', background: 'rgba(14,165,233, 0.1)', color: 'var(--accent-primary)', textDecoration: 'none'}}>
              <Cpu size={16} style={{marginRight: 10}}/> Open Temporal Server UI
            </a>
            
            <a href="http://localhost:8222" target="_blank" className="action-btn" style={{width: '100%', height: 'auto', padding: '12px 16px', borderRadius: '8px', justifyContent: 'flex-start', background: 'rgba(16,185,129, 0.1)', color: 'var(--success)', textDecoration: 'none'}}>
              <Network size={16} style={{marginRight: 10}}/> Open NATS Diagnostic
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}


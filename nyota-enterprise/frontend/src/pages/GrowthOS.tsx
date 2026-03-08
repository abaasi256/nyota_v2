import { useState, useEffect } from 'react';
import { Search, PenTool, Link, PlusCircle, RefreshCw } from 'lucide-react';

interface ContentBrief {
  keyword_id: string;
  title: string;
  status: string;
  content_length: number;
  created_at: string;
}

export default function GrowthOS() {
  const [briefs, setBriefs] = useState<ContentBrief[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBriefs = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/growth/content_briefs');
      const data = await response.json();
      setBriefs(data);
    } catch (err) {
      console.error('Failed to fetch growth briefs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerCrawl = async () => {
    const keyword = prompt("Enter target keyword for AI SERP Crawl & Generation:");
    if (!keyword) return;
    try {
      const res = await fetch('http://localhost:8000/bus/publish/orchestrator/start_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: "start",
          target: "system",
          data: {
            target_keyword: keyword
          }
        })
      });
      if (res.ok) {
        alert(`Successfully dispatched crawler sequence for: ${keyword}`);
        fetchBriefs(); // Poll again immediately
      } else {
        alert("Failed to reach Core Gateway");
      }
    } catch (err) {
      console.error(err);
      alert("Network error orchestrating swarm.");
    }
  };

  useEffect(() => {
    fetchBriefs();
    const interval = setInterval(fetchBriefs, 10000); // Live poll every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div className="metric-grid">
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Zuri Crawler Status</span>
            <Search size={16} />
          </div>
          <div className="metric-value">Active <span style={{fontSize: 14, color: 'var(--success)'}}>Listening</span></div>
          <div className="metric-trend">NATS Trigger Driven</div>
        </div>
        
        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Amani Drafter Stats</span>
            <PenTool size={16} />
          </div>
          <div className="metric-value">{briefs.length} <span style={{fontSize: 14, color: 'var(--text-muted)'}}>Generated DB Briefs</span></div>
          <div className="metric-trend trend-up">Avg size: {briefs.length > 0 ? Math.round(briefs.reduce((acc, curr) => acc + curr.content_length, 0) / briefs.length) : 0} bytes</div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-header">
            <span className="metric-title">Avg Domain Strength</span>
            <Link size={16} />
          </div>
          <div className="metric-value">DR 48</div>
          <div className="metric-trend trend-up">↑ +2 this month</div>
        </div>
      </div>

      <div className="panel glass-panel" style={{marginBottom: 24}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
          <h2 className="panel-title" style={{margin: 0}}>Latest AI Content Generation (Live DB)</h2>
          <div style={{display: 'flex', gap: 12}}>
            <button className="action-btn" onClick={fetchBriefs} style={{borderRadius: 8, height: 36, width: 36}}>
              <RefreshCw size={16} className={loading ? "spin" : ""} />
            </button>
            <button onClick={handleTriggerCrawl} className="action-btn" style={{width: 'auto', padding: '0 16px', borderRadius: '8px', background: 'var(--accent-primary)', color: '#fff', border: 'none', cursor: 'pointer'}}>
              <PlusCircle size={16} style={{marginRight: 8}}/> Trigger Manual Crawl
            </button>
          </div>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Generated Title</th>
              <th>Document Size</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {briefs.map((brief, idx) => (
              <tr key={idx}>
                <td className="text-mono" style={{fontSize: 11}}>{brief.keyword_id.substring(0, 13)}...</td>
                <td>{brief.title}</td>
                <td>{(brief.content_length / 1024).toFixed(2)} KB</td>
                <td style={{color: 'var(--text-muted)'}}>{new Date(brief.created_at).toLocaleString()}</td>
                <td>
                  <span className={`status-badge ${brief.status === 'DRAFTED' ? 'status-active' : 'status-pending'}`}>
                    {brief.status}
                  </span>
                </td>
              </tr>
            ))}
            {briefs.length === 0 && !loading && (
              <tr>
                <td colSpan={5} style={{textAlign: 'center', padding: '32px', color: 'var(--text-muted)'}}>No content briefs generated yet. Trigger a workflow.</td>
              </tr>
            )}
            {loading && briefs.length === 0 && (
              <tr>
                <td colSpan={5} style={{textAlign: 'center', padding: '32px', color: 'var(--text-muted)'}}>Connecting to Core DB...</td>
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

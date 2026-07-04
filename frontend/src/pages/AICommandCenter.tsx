import { useState } from 'react';
import {
  Search, BrainCircuit, AlertTriangle, ShieldCheck,
  TrendingDown, Target, Zap, FileText, Loader2,
  CheckCircle, BarChart3, DollarSign, MapPin, Lightbulb,
} from 'lucide-react';

interface AnalysisResult {
  risk_score: number;
  confidence: string;
  evidence: string[];
  recommendation: string;
  affected_areas: string[];
  priority: string;
  resources_needed: string[];
  estimated_cost: string;
  estimated_savings: string;
  executive_summary: string;
}

const suggestedQueries = [
  'What should I focus on today?',
  'Which area is at highest risk right now?',
  'What happens if rainfall increases by 30%?',
  'What resources should I deploy to Ward 2?',
  'Show me the flood risk assessment',
];

const AICommandCenter = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const runAnalysis = (q?: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    setQuery(searchQuery);
    setLoading(true);

    fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: searchQuery }),
    })
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data) {
          setResult(json.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Analysis error:', err);
        setLoading(false);
      });
  };

  const downloadReport = () => {
    fetch('http://localhost:8000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'Emergency Risk Assessment' }),
    })
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data && json.data.download_url) {
          window.open(json.data.download_url, '_blank');
        }
      })
      .catch(err => console.error('Error generating PDF report:', err));
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <BrainCircuit size={20} className="text-primary" />
          </div>
          AI Command Center
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Ask complex questions about city operations. Get actionable intelligence.</p>
      </div>

      {/* Search */}
      <div className="glass rounded-xl p-6 glow-primary">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" size={20} />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && runAnalysis()}
            className="w-full bg-white/[0.03] border border-border text-text-primary rounded-xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:border-primary/40 transition-all placeholder-text-muted"
            placeholder="Ask the AI: 'What should I focus on today?' or 'Which area is at highest risk?'"
          />
        </div>

        {/* Suggested Queries */}
        <div className="flex flex-wrap gap-2 mt-4">
          {suggestedQueries.map((sq) => (
            <button
              key={sq}
              onClick={() => runAnalysis(sq)}
              className="px-3 py-1.5 rounded-lg bg-white/[0.03] border border-border text-xs text-text-secondary hover:text-text-primary hover:border-border-hover transition-all"
            >
              {sq}
            </button>
          ))}
        </div>

        <button
          onClick={() => runAnalysis()}
          disabled={loading || !query.trim()}
          className="mt-4 w-full bg-primary hover:bg-primary-light text-white font-medium text-sm py-3.5 rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? (
            <><Loader2 className="animate-spin" size={18} /> Analyzing city data...</>
          ) : (
            <><Zap size={16} /> Run City Analysis</>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 fade-in">
          {/* Left Column — Main Content */}
          <div className="lg:col-span-2 space-y-4">
            {/* Recommendation */}
            <div className="glass rounded-xl p-5 border-l-2 border-l-primary">
              <div className="flex items-center gap-2 mb-3">
                <Target size={16} className="text-primary" />
                <h3 className="text-sm font-semibold text-text-primary">Recommendation</h3>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed">{result.recommendation}</p>
            </div>

            {/* Evidence */}
            <div className="glass rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <ShieldCheck size={16} className="text-success" />
                <h3 className="text-sm font-semibold text-text-primary">Evidence & Data Points</h3>
              </div>
              <div className="space-y-2.5">
                {result.evidence.map((e, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm text-text-secondary">
                    <CheckCircle className="text-success/60 shrink-0 mt-0.5" size={14} />
                    <span>{e}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Executive Summary */}
            <div className="glass rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb size={16} className="text-warning" />
                <h3 className="text-sm font-semibold text-text-primary">Executive Summary</h3>
              </div>
              <p className="text-sm text-text-muted leading-relaxed">{result.executive_summary}</p>
              <button 
                onClick={downloadReport}
                className="mt-4 flex items-center gap-2 text-xs text-primary-light hover:text-primary font-medium transition-colors"
              >
                <FileText size={14} /> Generate Formal PDF Report
              </button>
            </div>
          </div>

          {/* Right Column — Metrics */}
          <div className="space-y-4">
            {/* Score Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="glass rounded-xl p-4 text-center">
                <p className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Risk Score</p>
                <p className="text-3xl font-bold text-danger">{result.risk_score}</p>
                <p className="text-[10px] text-text-muted mt-0.5">/ 100</p>
              </div>
              <div className="glass rounded-xl p-4 text-center">
                <p className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Confidence</p>
                <p className="text-3xl font-bold text-success">{result.confidence}</p>
                <p className="text-[10px] text-text-muted mt-0.5">accuracy</p>
              </div>
            </div>

            {/* Priority */}
            <div className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle size={14} className="text-warning" />
                <p className="text-xs font-semibold text-text-primary">Priority Level</p>
              </div>
              <div className="inline-block px-3 py-1.5 bg-danger/10 text-danger border border-danger/20 rounded-lg text-xs font-bold tracking-widest">
                {result.priority}
              </div>
            </div>

            {/* Affected Areas */}
            <div className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <MapPin size={14} className="text-info" />
                <p className="text-xs font-semibold text-text-primary">Affected Areas</p>
              </div>
              <div className="flex gap-1.5 flex-wrap">
                {result.affected_areas.map(a => (
                  <span key={a} className="px-2.5 py-1 bg-white/[0.04] border border-border rounded-md text-xs text-text-secondary">{a}</span>
                ))}
              </div>
            </div>

            {/* Resources */}
            <div className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <BarChart3 size={14} className="text-primary" />
                <p className="text-xs font-semibold text-text-primary">Resources Needed</p>
              </div>
              <ul className="space-y-1.5 text-xs text-text-secondary">
                {result.resources_needed.map(r => (
                  <li key={r} className="flex items-center gap-2">
                    <div className="w-1 h-1 rounded-full bg-primary" />
                    {r}
                  </li>
                ))}
              </ul>
            </div>

            {/* Cost */}
            <div className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <DollarSign size={14} className="text-success" />
                <p className="text-xs font-semibold text-text-primary">Cost Analysis</p>
              </div>
              <div className="space-y-2">
                <div>
                  <p className="text-[10px] text-text-muted uppercase tracking-wider">Deployment Cost</p>
                  <p className="text-sm font-semibold text-text-primary">{result.estimated_cost}</p>
                </div>
                <div className="pt-2 border-t border-border">
                  <p className="text-[10px] text-text-muted uppercase tracking-wider">Estimated Savings</p>
                  <p className="text-sm font-semibold text-success flex items-center gap-1">
                    <TrendingDown size={12} /> {result.estimated_savings}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AICommandCenter;

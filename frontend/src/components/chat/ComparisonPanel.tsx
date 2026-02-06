import { SearchMetrics, SearchResponse } from '@/lib/api';

interface ComparisonPanelProps {
  response: SearchResponse | null;
}

function formatPercent(value?: number | null) {
  if (value === undefined || value === null) return '-';
  return `${(value * 100).toFixed(1)}%`;
}

function formatMs(value?: number | null) {
  if (value === undefined || value === null) return '-';
  return `${value.toFixed(1)} ms`;
}

function MetricBars({ label, classical, quantum }: { label: string; classical?: number | null; quantum?: number | null }) {
  const classicalWidth = classical ? Math.max(0, Math.min(1, classical)) * 100 : 0;
  const quantumWidth = quantum ? Math.max(0, Math.min(1, quantum)) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span>{formatPercent(classical)} | {formatPercent(quantum)}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div className="h-full bg-emerald-400" style={{ width: `${classicalWidth}%` }} />
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div className="h-full bg-sky-400" style={{ width: `${quantumWidth}%` }} />
        </div>
      </div>
    </div>
  );
}

function MetricsSummary({ title, metrics }: { title: string; metrics?: SearchMetrics }) {
  if (!metrics) {
    return (
      <div className="rounded-xl border border-border bg-card p-4">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground mt-2">Sem metricas disponiveis.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <p className="text-sm font-medium">{title}</p>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Latencia</span>
        <span>{formatMs(metrics.latency_ms)}</span>
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>K</span>
        <span>{metrics.k}</span>
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Candidatos</span>
        <span>{metrics.candidate_k}</span>
      </div>
    </div>
  );
}

export function ComparisonPanel({ response }: ComparisonPanelProps) {
  if (!response) return null;

  const comparison = response.comparison;
  const showComparison = Boolean(comparison);
  const classicalMetrics = comparison?.classical.metrics ?? response.metrics;
  const quantumMetrics = comparison?.quantum.metrics;
  const hasLabels = Boolean(classicalMetrics?.has_labels || quantumMetrics?.has_labels);

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-6">
      <div className="rounded-2xl border border-border bg-background/80 p-4 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-sm font-semibold">Comparacao de Busca</p>
            <p className="text-xs text-muted-foreground">Classico vs Quantico (PennyLane)</p>
          </div>
          <span className="text-xs text-muted-foreground">Modo: {response.mode}</span>
        </div>

        {showComparison ? (
          <div className="grid gap-3 md:grid-cols-2">
            <MetricsSummary title="Classico" metrics={comparison?.classical.metrics} />
            <MetricsSummary title="Quantico" metrics={comparison?.quantum.metrics} />
          </div>
        ) : (
          <MetricsSummary title="Resultado" metrics={response.metrics} />
        )}

        {showComparison && hasLabels && (
          <div className="space-y-4">
            <MetricBars
              label={`Recall@${comparison?.classical.metrics?.k ?? classicalMetrics?.k ?? 5}`}
              classical={comparison?.classical.metrics?.recall_at_k}
              quantum={comparison?.quantum.metrics?.recall_at_k}
            />
            <MetricBars
              label="MRR"
              classical={comparison?.classical.metrics?.mrr}
              quantum={comparison?.quantum.metrics?.mrr}
            />
            <MetricBars
              label={`NDCG@${comparison?.classical.metrics?.k ?? classicalMetrics?.k ?? 5}`}
              classical={comparison?.classical.metrics?.ndcg_at_k}
              quantum={comparison?.quantum.metrics?.ndcg_at_k}
            />
          </div>
        )}

        {showComparison && !hasLabels && (
          <p className="text-xs text-muted-foreground">
            As metricas de ranking aparecem apenas quando a consulta possui rotulos de relevancia.
          </p>
        )}
      </div>
    </div>
  );
}

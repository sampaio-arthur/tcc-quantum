import { SearchResponse } from '@/lib/api';

interface PipelinePanelProps {
  response: SearchResponse | null;
}

function formatPercent(value?: number | null) {
  if (value === undefined || value === null) return '-';
  return (value * 100).toFixed(1) + '%';
}

function DeltaRow({ label, classical, quantum }: { label: string; classical?: number | null; quantum?: number | null }) {
  const hasValues = classical !== undefined && classical !== null && quantum !== undefined && quantum !== null;
  const delta = hasValues ? quantum - classical : null;
  const deltaText = delta === null ? '-' : (delta >= 0 ? '+' : '') + (delta * 100).toFixed(1) + ' p.p.';

  return (
    <div className='rounded-lg border border-border bg-card px-3 py-2 text-xs'>
      <div className='text-muted-foreground'>{label}</div>
      <div className='mt-1 grid grid-cols-3 gap-2 text-foreground'>
        <span>C: {formatPercent(classical)}</span>
        <span>Q: {formatPercent(quantum)}</span>
        <span>Delta: {deltaText}</span>
      </div>
    </div>
  );
}

export function PipelinePanel({ response }: PipelinePanelProps) {
  if (!response?.comparison) return null;

  const classical = response.comparison.classical.metrics;
  const quantum = response.comparison.quantum.metrics;
  const kValue = classical?.k ?? quantum?.k ?? 5;
  const hasLabels = Boolean(classical?.has_labels || quantum?.has_labels);
  const hasIdealAnswer = Boolean(classical?.has_ideal_answer || quantum?.has_ideal_answer);

  return (
    <div className='w-full max-w-3xl mx-auto px-4 pb-4'>
      <div className='rounded-2xl border border-border bg-background/80 p-4 space-y-4'>
        <div>
          <p className='text-sm font-semibold'>Pipeline de Acuracia</p>
          <p className='text-xs text-muted-foreground'>Comparacao classico vs quantico com base no gabarito da consulta</p>
        </div>

        {(hasLabels || hasIdealAnswer) ? (
          <div className='grid gap-2'>
            <DeltaRow label={'Accuracy@' + kValue} classical={classical?.accuracy_at_k} quantum={quantum?.accuracy_at_k} />
            <DeltaRow label={'Recall@' + kValue} classical={classical?.recall_at_k} quantum={quantum?.recall_at_k} />
            <DeltaRow label='MRR' classical={classical?.mrr} quantum={quantum?.mrr} />
            <DeltaRow label={'NDCG@' + kValue} classical={classical?.ndcg_at_k} quantum={quantum?.ndcg_at_k} />
            <DeltaRow label='Similaridade resposta ideal' classical={classical?.answer_similarity} quantum={quantum?.answer_similarity} />
          </div>
        ) : (
          <p className='text-xs text-muted-foreground'>
            Esta consulta nao possui gabarito salvo. Cadastre pergunta + resposta ideal para comparar acuracia.
          </p>
        )}
      </div>
    </div>
  );
}

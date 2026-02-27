import { SearchAlgorithmDetails, SearchResponse } from '@/lib/api';

interface ComparisonPanelProps {
  response: SearchResponse | null;
}

function StepByStep({ title, details }: { title: string; details?: SearchAlgorithmDetails }) {
  const rawSteps = details?.debug?.steps;
  const steps = Array.isArray(rawSteps) ? rawSteps.filter((x): x is string => typeof x === 'string') : [];

  return (
    <div className='rounded-xl border border-border bg-card p-4 space-y-2'>
      <p className='text-sm font-medium'>{title}</p>
      {steps.length ? (
        <ol className='space-y-1 text-xs text-muted-foreground'>
          {steps.map((step, idx) => (
            <li key={`${title}-${idx}`}>
              <span className='text-foreground'>{idx + 1}.</span> {step}
            </li>
          ))}
        </ol>
      ) : (
        <p className='text-xs text-muted-foreground'>Passo a passo não disponível.</p>
      )}
    </div>
  );
}

export function ComparisonPanel({ response }: ComparisonPanelProps) {
  if (!response) return null;

  const comparison = response.comparison;
  const showComparison = Boolean(comparison);
  const classicalResults = comparison?.classical.results ?? response.results ?? [];
  const quantumResults = comparison?.quantum.results ?? [];
  const classicalMetrics = comparison?.classical.metrics;
  const quantumMetrics = comparison?.quantum.metrics;
  const hasIrLabels = Boolean(classicalMetrics?.has_labels || quantumMetrics?.has_labels);
  const irObservation = hasIrLabels
    ? 'Calculado com gabarito (qrels).'
    : 'Requer gabarito (qrels) para calcular.';

  return (
    <div className='w-full max-w-3xl mx-auto px-4 pb-6'>
      <div className='rounded-2xl border border-border bg-background/80 p-4 space-y-4'>
        <div className='flex flex-wrap items-center justify-between gap-2'>
          <div>
            <p className='text-sm font-semibold'>Comparação de Busca</p>
            <p className='text-xs text-muted-foreground'>Objetivo: comparar acurácia e velocidade. Comparação justa: mesmos métodos e mesma análise, mudando apenas a representação vetorial.</p>
          </div>
          <span className='text-xs text-muted-foreground'>Modo: {response.mode}</span>
        </div>

        {showComparison ? (
          <div className='grid gap-3 md:grid-cols-2'>
            <StepByStep title='Passo a passo: Clássico' details={comparison?.classical.algorithm_details} />
            <StepByStep title='Passo a passo: Quântico' details={comparison?.quantum.algorithm_details} />
          </div>
        ) : (
          <StepByStep title='Passo a passo' details={response.algorithm_details} />
        )}

        {showComparison && (
          <div className='rounded-xl border border-border bg-card p-4'>
            <p className='text-sm font-medium mb-3'>Tabela Comparativa (efetividade + custo)</p>
            <div className='overflow-x-auto'>
              <table className='w-full text-xs'>
                <thead>
                  <tr className='text-left text-muted-foreground border-b border-border'>
                    <th className='py-2 pr-3'>Métrica</th>
                    <th className='py-2 pr-3'>Clássico</th>
                    <th className='py-2 pr-3'>Quântico</th>
                    <th className='py-2'>Observação</th>
                  </tr>
                </thead>
                <tbody className='text-muted-foreground'>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Latência (ms)</td>
                    <td className='py-2 pr-3'>{classicalMetrics?.latency_ms?.toFixed(1) ?? '-'}</td>
                    <td className='py-2 pr-3'>{quantumMetrics?.latency_ms?.toFixed(1) ?? '-'}</td>
                    <td className='py-2'>Comparativo de custo/tempo (não é qualidade)</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Docs recuperados</td>
                    <td className='py-2 pr-3'>{classicalResults.length}</td>
                    <td className='py-2 pr-3'>{quantumResults.length}</td>
                    <td className='py-2'>Top-k retornado por pipeline</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Precision@k</td>
                    <td className='py-2 pr-3'>{typeof classicalMetrics?.precision_at_k === 'number' ? classicalMetrics.precision_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2 pr-3'>{typeof quantumMetrics?.precision_at_k === 'number' ? quantumMetrics.precision_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2'>{irObservation}</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Recall@k</td>
                    <td className='py-2 pr-3'>{typeof classicalMetrics?.recall_at_k === 'number' ? classicalMetrics.recall_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2 pr-3'>{typeof quantumMetrics?.recall_at_k === 'number' ? quantumMetrics.recall_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2'>{irObservation}</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>NDCG@k</td>
                    <td className='py-2 pr-3'>{typeof classicalMetrics?.ndcg_at_k === 'number' ? classicalMetrics.ndcg_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2 pr-3'>{typeof quantumMetrics?.ndcg_at_k === 'number' ? quantumMetrics.ndcg_at_k.toFixed(3) : '-'}</td>
                    <td className='py-2'>{irObservation}</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Spearman</td>
                    <td className='py-2 pr-3'>{typeof classicalMetrics?.spearman === 'number' ? classicalMetrics.spearman.toFixed(3) : '-'}</td>
                    <td className='py-2 pr-3'>{typeof quantumMetrics?.spearman === 'number' ? quantumMetrics.spearman.toFixed(3) : '-'}</td>
                    <td className='py-2'>{irObservation}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        <p className='text-xs text-muted-foreground'>
          {hasIrLabels
            ? 'Métricas IR reais exibidas para esta query com gabarito (qrels) encontrado.'
            : 'Sem gabarito correspondente para esta query no chat. Para métricas IR canônicas, use queries do BEIR (query_id) ou avaliação batch.'}
        </p>
      </div>
    </div>
  );
}

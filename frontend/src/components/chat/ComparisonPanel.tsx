import { SearchAlgorithmDetails, SearchResponse } from '@/lib/api';

interface ComparisonPanelProps {
  response: SearchResponse | null;
}

function AlgorithmSummary({ title, details }: { title: string; details?: SearchAlgorithmDetails }) {
  if (!details) {
    return (
      <div className='rounded-xl border border-border bg-card p-4'>
        <p className='text-sm font-medium'>{title}</p>
        <p className='text-xs text-muted-foreground mt-2'>Detalhes do algoritmo nao disponiveis.</p>
      </div>
    );
  }

  return (
    <div className='rounded-xl border border-border bg-card p-4 space-y-2'>
      <p className='text-sm font-medium'>{title}</p>
      <div className='text-xs text-muted-foreground'>
        <span className='text-foreground'>Comparador:</span> {details.comparator}
      </div>
      <div className='text-xs text-muted-foreground'>
        <span className='text-foreground'>Candidatos:</span> {details.candidate_strategy}
      </div>
      <p className='text-xs text-muted-foreground'>{details.description}</p>
    </div>
  );
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
        <p className='text-xs text-muted-foreground'>Passo a passo nao disponivel.</p>
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
  const comparative = response.comparison_metrics;

  return (
    <div className='w-full max-w-3xl mx-auto px-4 pb-6'>
      <div className='rounded-2xl border border-border bg-background/80 p-4 space-y-4'>
        <div className='flex flex-wrap items-center justify-between gap-2'>
          <div>
            <p className='text-sm font-semibold'>Comparacao de Busca</p>
            <p className='text-xs text-muted-foreground'>Classico vs Quantico (PennyLane)</p>
          </div>
          <span className='text-xs text-muted-foreground'>Modo: {response.mode}</span>
        </div>

        {showComparison ? (
          <div className='grid gap-3 md:grid-cols-2'>
            <StepByStep title='Passo a passo: Classico' details={comparison?.classical.algorithm_details} />
            <StepByStep title='Passo a passo: Quantico' details={comparison?.quantum.algorithm_details} />
          </div>
        ) : (
          <StepByStep title='Passo a passo' details={response.algorithm_details} />
        )}

        {showComparison && (
          <div className='rounded-xl border border-border bg-card p-4'>
            <p className='text-sm font-medium mb-3'>Tabela Comparativa (proxy de efetividade + custo)</p>
            <div className='overflow-x-auto'>
              <table className='w-full text-xs'>
                <thead>
                  <tr className='text-left text-muted-foreground border-b border-border'>
                    <th className='py-2 pr-3'>Metrica</th>
                    <th className='py-2 pr-3'>Classico</th>
                    <th className='py-2 pr-3'>Quantico</th>
                    <th className='py-2'>Observacao</th>
                  </tr>
                </thead>
                <tbody className='text-muted-foreground'>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Latencia (ms)</td>
                    <td className='py-2 pr-3'>{classicalMetrics?.latency_ms?.toFixed(1) ?? '-'}</td>
                    <td className='py-2 pr-3'>{quantumMetrics?.latency_ms?.toFixed(1) ?? '-'}</td>
                    <td className='py-2'>Comparativo de custo/tempo (nao e qualidade)</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Mean score@k</td>
                    <td className='py-2 pr-3'>{typeof comparative?.classical_mean_score === 'number' ? comparative.classical_mean_score.toFixed(3) : '-'}</td>
                    <td className='py-2 pr-3'>{typeof comparative?.quantum_mean_score === 'number' ? comparative.quantum_mean_score.toFixed(3) : '-'}</td>
                    <td className='py-2'>Comparavel apenas dentro deste setup (espacos vetoriais diferentes)</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Docs recuperados</td>
                    <td className='py-2 pr-3'>{classicalResults.length}</td>
                    <td className='py-2 pr-3'>{quantumResults.length}</td>
                    <td className='py-2'>Top-k retornado por pipeline</td>
                  </tr>
                  <tr className='border-b border-border/60'>
                    <td className='py-2 pr-3 text-foreground'>Overlap@k</td>
                    <td className='py-2 pr-3' colSpan={2}>{comparative?.overlap_at_k ?? '-'}</td>
                    <td className='py-2'>Interseccao entre rankings classico e quantico</td>
                  </tr>
                  <tr>
                    <td className='py-2 pr-3 text-foreground'>Jaccard@k</td>
                    <td className='py-2 pr-3' colSpan={2}>
                      {typeof comparative?.jaccard_at_k === 'number' ? (comparative.jaccard_at_k * 100).toFixed(1) + '%' : '-'}
                    </td>
                    <td className='py-2'>Similaridade entre conjuntos recuperados</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {showComparison ? (
          <div className='grid gap-3 md:grid-cols-2'>
            <div className='rounded-xl border border-border bg-card p-4 space-y-2'>
              <p className='text-sm font-medium'>Resultados recuperados: Classico</p>
              {classicalResults.length ? classicalResults.slice(0, 5).map((item, idx) => (
                <div key={`c-${item.doc_id}-${idx}`} className='text-xs text-muted-foreground'>
                  <span className='text-foreground'>{idx + 1}.</span> score={item.score.toFixed(3)}
                </div>
              )) : <p className='text-xs text-muted-foreground'>Nenhum documento recuperado.</p>}
            </div>
            <div className='rounded-xl border border-border bg-card p-4 space-y-2'>
              <p className='text-sm font-medium'>Resultados recuperados: Quantico</p>
              {quantumResults.length ? quantumResults.slice(0, 5).map((item, idx) => (
                <div key={`q-${item.doc_id}-${idx}`} className='text-xs text-muted-foreground'>
                  <span className='text-foreground'>{idx + 1}.</span> score={item.score.toFixed(3)}
                </div>
              )) : <p className='text-xs text-muted-foreground'>Nenhum documento recuperado.</p>}
            </div>
          </div>
        ) : (
          <div className='rounded-xl border border-border bg-card p-4 space-y-2'>
            <p className='text-sm font-medium'>Resultados recuperados</p>
            {(response.results ?? []).slice(0, 5).map((item, idx) => (
              <div key={`r-${item.doc_id}-${idx}`} className='text-xs text-muted-foreground'>
                <span className='text-foreground'>{idx + 1}.</span> score={item.score.toFixed(3)}
              </div>
            ))}
          </div>
        )}

        {showComparison ? (
          <div className='grid gap-3 md:grid-cols-2'>
            <AlgorithmSummary title='Como funciona: Classico' details={comparison?.classical.algorithm_details} />
            <AlgorithmSummary title='Como funciona: Quantico' details={comparison?.quantum.algorithm_details} />
          </div>
        ) : (
          <AlgorithmSummary title='Como funciona' details={response.algorithm_details} />
        )}

        <p className='text-xs text-muted-foreground'>
          O chat exibe proxies comparativos (latencia, overlap e scores) sem gabarito. Para metricas de IR canonicas (precision/recall/NDCG/Spearman), use avaliacao batch com ground truth.
        </p>
      </div>
    </div>
  );
}

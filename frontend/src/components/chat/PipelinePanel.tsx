import { SearchAlgorithmDetails, SearchResponse } from '@/lib/api';

interface PipelinePanelProps {
  response: SearchResponse | null;
}

function AlgoLine({ label, details }: { label: string; details?: SearchAlgorithmDetails }) {
  return (
    <div className='rounded-lg border border-border bg-card px-3 py-2 text-xs'>
      <div className='text-muted-foreground'>{label}</div>
      <div className='mt-1 text-foreground'>
        {details ? details.comparator + ' | ' + details.candidate_strategy : 'Sem detalhes de algoritmo'}
      </div>
    </div>
  );
}

export function PipelinePanel({ response }: PipelinePanelProps) {
  if (!response?.comparison) return null;

  const classicalCount = response.comparison.classical.results?.length ?? 0;
  const quantumCount = response.comparison.quantum.results?.length ?? 0;
  const overlap = response.comparison_metrics?.overlap_at_k ?? new Set(
    (response.comparison.classical.results ?? [])
      .map((item) => item.doc_id)
      .filter((id) => (response.comparison.quantum.results ?? []).some((q) => q.doc_id === id))
  ).size;
  const classicalLatency = response.comparison.classical.metrics?.latency_ms;
  const quantumLatency = response.comparison.quantum.metrics?.latency_ms;

  return (
    <div className='w-full max-w-3xl mx-auto px-4 pb-4'>
      <div className='rounded-2xl border border-border bg-background/80 p-4 space-y-4'>
        <div>
          <p className='text-sm font-semibold'>Pipeline de Retrieval</p>
          <p className='text-xs text-muted-foreground'>Comparacao classico vs quantico sobre o dataset Reuters (sem gabarito no fluxo do chat)</p>
        </div>

        <div className='grid gap-2'>
          <AlgoLine label='Fluxo classico' details={response.comparison.classical.algorithm_details} />
          <AlgoLine label='Fluxo quantico' details={response.comparison.quantum.algorithm_details} />
        </div>

        <div className='grid gap-2'>
          <div className='rounded-lg border border-border bg-card px-3 py-2 text-xs'>
            <div className='text-muted-foreground'>Resumo da recuperacao</div>
            <div className='mt-1 text-foreground'>
              Classico: {classicalCount} docs | Quantico: {quantumCount} docs | Sobreposicao top-k: {overlap}
            </div>
            {(classicalLatency !== undefined && quantumLatency !== undefined) && (
              <div className='mt-1 text-muted-foreground'>
                Latencia: classico {classicalLatency.toFixed(1)} ms | quantico {quantumLatency.toFixed(1)} ms
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

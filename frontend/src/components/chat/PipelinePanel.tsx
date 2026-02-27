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
  const classicalLatency = response.comparison.classical.metrics?.latency_ms;
  const quantumLatency = response.comparison.quantum.metrics?.latency_ms;

  return (
    <div className='w-full max-w-3xl mx-auto px-4 pb-4'>
      <div className='rounded-2xl border border-border bg-background/80 p-4 space-y-4'>
        <div>
          <p className='text-sm font-semibold'>Pipeline de Retrieval</p>
          <p className='text-xs text-muted-foreground'>Comparação de acurácia e velocidade no BEIR. Comparação justa: mesmos métodos e mesma análise; a diferença principal está na representação vetorial (embedding clássico vs vetor quântico-inspirado).</p>
        </div>

        <div className='grid gap-2'>
          <AlgoLine label='Fluxo clássico' details={response.comparison.classical.algorithm_details} />
          <AlgoLine label='Fluxo quântico' details={response.comparison.quantum.algorithm_details} />
        </div>

        <div className='grid gap-2'>
          <div className='rounded-lg border border-border bg-card px-3 py-2 text-xs'>
            <div className='text-muted-foreground'>Resumo da recuperação</div>
            <div className='mt-1 text-foreground'>
              Clássico: {classicalCount} docs | Quântico: {quantumCount} docs
            </div>
            {(classicalLatency !== undefined && quantumLatency !== undefined) && (
              <div className='mt-1 text-muted-foreground'>
                Latência: clássico {classicalLatency.toFixed(1)} ms | quântico {quantumLatency.toFixed(1)} ms
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

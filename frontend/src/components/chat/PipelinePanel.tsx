interface PipelinePanelProps {
  visible: boolean;
}

const classicalSteps = [
  'Extracao e chunking do documento',
  'Embeddings + cosine similarity',
  'Ranking classico',
  'Resultados finais',
];

const quantumSteps = [
  'Extracao e chunking do documento',
  'Embeddings + prefiltragem classica',
  'Swap test (PennyLane) nos candidatos',
  'Ranking quantico e comparacao',
];

function StepCard({ label, index }: { label: string; index: number }) {
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs text-foreground">
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">Etapa {index + 1}</div>
      <div className="mt-1 font-medium">{label}</div>
    </div>
  );
}

export function PipelinePanel({ visible }: PipelinePanelProps) {
  if (!visible) return null;

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-4">
      <div className="rounded-2xl border border-border bg-background/80 p-4 space-y-4">
        <div>
          <p className="text-sm font-semibold">Pipeline de Comparacao</p>
          <p className="text-xs text-muted-foreground">Fluxo classico vs quantico no mesmo dataset/documento</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <p className="text-xs font-semibold text-foreground">Classico</p>
            <div className="grid gap-2">
              {classicalSteps.map((step, index) => (
                <StepCard key={step} label={step} index={index} />
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-semibold text-foreground">Quantico</p>
            <div className="grid gap-2">
              {quantumSteps.map((step, index) => (
                <StepCard key={step} label={step} index={index} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

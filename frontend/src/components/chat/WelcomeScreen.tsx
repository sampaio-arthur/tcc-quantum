import { Sparkles } from 'lucide-react';

export function WelcomeScreen() {
  const frequentQueries = [
    'what is the origin of COVID-19',
    'how does the coronavirus respond to changes in the weather',
    'what causes death from Covid-19?',
    'what drugs have been active against SARS-CoV or SARS-CoV-2 in animal studies?',
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4">
      <div className="text-center fade-in max-w-3xl">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-success/20 to-success/5 mb-6">
          <Sparkles className="h-8 w-8 text-success" />
        </div>
        <h1 className="text-3xl font-semibold text-foreground mb-2">Por onde começamos?</h1>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Esta plataforma demonstra desempenho de busca semântica comparando acurácia e velocidade entre dois métodos: embeddings clássicos e vetor quântico-inspirado.
        </p>

        <div className="mt-8 rounded-xl border border-border bg-card/50 p-4 text-left">
          <p className="text-sm font-medium text-foreground mb-2">Como funciona</p>
          <p className="text-xs text-muted-foreground">
            1) Você envia a pergunta. 2) O sistema busca no corpus BEIR com dois pipelines. 3) A comparação é justa: ambos compartilham os mesmos métodos de busca e análise. 4) A diferença principal está na representação vetorial: embedding clássico vs vetor quântico-inspirado. 5) O painel mostra acurácia (quando há qrels) e velocidade.
          </p>
        </div>

        <div className="mt-4 rounded-xl border border-border bg-card/50 p-4 text-left">
          <p className="text-sm font-medium text-foreground mb-2">Queries frequentes para testar</p>
          <div className="grid gap-2">
            {frequentQueries.map((query) => (
              <div key={query} className="rounded-md border border-border px-3 py-2 text-xs text-muted-foreground">
                {query}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

import { Sparkles } from 'lucide-react';

export function WelcomeScreen() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4">
      <div className="text-center fade-in">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-success/20 to-success/5 mb-6">
          <Sparkles className="h-8 w-8 text-success" />
        </div>
        <h1 className="text-3xl font-semibold text-foreground mb-2">
          Por onde começamos?
        </h1>
        <p className="text-muted-foreground max-w-md">
          Faça uma pergunta ou anexe um arquivo para começar uma busca
        </p>
      </div>
    </div>
  );
}

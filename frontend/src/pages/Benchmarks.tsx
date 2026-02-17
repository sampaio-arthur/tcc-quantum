import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { api, BenchmarkLabel } from '@/lib/api';

const DEFAULT_DATASET_ID = 'mini-rag';

export default function Benchmarks() {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [activeDatasetId] = useState(DEFAULT_DATASET_ID);
  const [labels, setLabels] = useState<BenchmarkLabel[]>([]);
  const [isBusy, setIsBusy] = useState(false);

  const [queryText, setQueryText] = useState('');
  const [idealAnswer, setIdealAnswer] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!authLoading && !user) navigate('/auth');
  }, [authLoading, user, navigate]);

  useEffect(() => {
    if (!user) return;
    void loadLabels(activeDatasetId);
  }, [user]);

  const loadLabels = async (datasetId: string) => {
    setIsBusy(true);
    try {
      const savedLabels = await api.listBenchmarkLabels(datasetId);
      setLabels(savedLabels);
      setMessage('');
    } catch (error) {
      console.error(error);
      setMessage(error instanceof Error ? error.message : 'Erro ao carregar gabaritos');
    } finally {
      setIsBusy(false);
    }
  };

  const handleSave = async () => {
    if (!queryText.trim() || !idealAnswer.trim()) {
      setMessage('Preencha pergunta e resposta ideal.');
      return;
    }

    setIsBusy(true);
    try {
      await api.upsertBenchmarkLabel({
        dataset_id: activeDatasetId,
        query_text: queryText.trim(),
        ideal_answer: idealAnswer.trim(),
      });
      await loadLabels(activeDatasetId);
      setQueryText('');
      setIdealAnswer('');
      setMessage('Gabarito salvo com sucesso.');
    } catch (error) {
      console.error(error);
      setMessage(error instanceof Error ? error.message : 'Erro ao salvar gabarito');
    } finally {
      setIsBusy(false);
    }
  };

  const handleDelete = async (item: BenchmarkLabel) => {
    setIsBusy(true);
    try {
      await api.deleteBenchmarkLabel(item.dataset_id, item.benchmark_id);
      await loadLabels(item.dataset_id);
      setMessage('Gabarito removido.');
    } catch (error) {
      console.error(error);
      setMessage(error instanceof Error ? error.message : 'Erro ao remover gabarito');
    } finally {
      setIsBusy(false);
    }
  };

  if (authLoading) {
    return <div className='min-h-screen bg-background' />;
  }

  return (
    <div className='min-h-screen bg-background text-foreground'>
      <div className='max-w-5xl mx-auto px-4 py-6 space-y-6'>
        <div className='flex items-center justify-between gap-3'>
          <div>
            <h1 className='text-2xl font-semibold'>Gabaritos de Acuracia</h1>
            <p className='text-sm text-muted-foreground'>
              Cadastre pergunta e resposta ideal. O sistema infere docs relevantes para medir ranking e precisao classico vs quantico.
            </p>
          </div>
          <Button variant='outline' onClick={() => navigate('/chat')}>Voltar ao Chat</Button>
        </div>

        <div className='rounded-xl border border-border p-4 space-y-4'>
          <div className='space-y-1'>
            <p className='text-sm font-medium'>Dataset padrao</p>
            <p className='text-sm text-muted-foreground'>{activeDatasetId}</p>
          </div>

          <div className='space-y-2'>
            <label className='text-sm font-medium'>Pergunta a avaliar</label>
            <textarea
              className='w-full bg-background border border-border rounded-md px-3 py-2 text-sm min-h-24'
              placeholder='Ex: qual o impacto das nanoparticulas?'
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
            />
          </div>

          <div className='space-y-2'>
            <label className='text-sm font-medium'>Resposta ideal (gabarito)</label>
            <textarea
              className='w-full bg-background border border-border rounded-md px-3 py-2 text-sm min-h-32'
              placeholder='Descreva a resposta esperada para comparar a qualidade da resposta gerada.'
              value={idealAnswer}
              onChange={(e) => setIdealAnswer(e.target.value)}
            />
          </div>

          <div className='flex items-center gap-2'>
            <Button onClick={handleSave} disabled={isBusy}>Salvar gabarito</Button>
            <Button variant='outline' onClick={() => activeDatasetId && loadLabels(activeDatasetId)} disabled={isBusy}>Atualizar lista</Button>
          </div>

          {message && <p className='text-sm text-muted-foreground'>{message}</p>}
        </div>

        <div className='rounded-xl border border-border p-4 space-y-3'>
          <h2 className='text-lg font-medium'>Gabaritos salvos</h2>
          {labels.length === 0 ? (
            <p className='text-sm text-muted-foreground'>Nenhum gabarito salvo para este dataset.</p>
          ) : (
            <div className='space-y-2'>
              {labels.map((item) => (
                <div key={item.dataset_id + ':' + item.benchmark_id} className='rounded-lg border border-border p-3'>
                  <div className='flex items-start justify-between gap-2'>
                    <div className='space-y-1'>
                      <p className='text-sm font-semibold'>Pergunta</p>
                      <p className='text-sm text-muted-foreground'>{item.query_text}</p>
                      <p className='text-sm font-semibold pt-2'>Resposta ideal</p>
                      <p className='text-sm text-muted-foreground whitespace-pre-wrap'>{item.ideal_answer}</p>
                      <p className='text-xs text-muted-foreground pt-1'>Docs relevantes inferidos: {item.relevant_doc_ids.length}</p>
                    </div>
                    <Button variant='destructive' size='sm' onClick={() => handleDelete(item)} disabled={isBusy}>Excluir</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

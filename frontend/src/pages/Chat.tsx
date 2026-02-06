import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList } from '@/components/chat/MessageList';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { ComparisonPanel } from '@/components/chat/ComparisonPanel';
import { useAuth } from '@/contexts/AuthContext';
import { api, Conversation, DatasetDetail, DatasetSummary, Message, SearchResponse } from '@/lib/api';

export default function Chat() {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const [source, setSource] = useState<'file' | 'dataset'>('file');
  const [mode, setMode] = useState<'classical' | 'quantum' | 'compare'>('compare');

  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [datasetDetail, setDatasetDetail] = useState<DatasetDetail | null>(null);
  const [selectedQueryId, setSelectedQueryId] = useState('');

  const [lastResponse, setLastResponse] = useState<SearchResponse | null>(null);

  // Redirect to auth if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth');
    }
  }, [user, authLoading, navigate]);

  // Load conversations
  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  useEffect(() => {
    api.getDatasets()
      .then(setDatasets)
      .catch((error) => {
        console.error('Error loading datasets:', error);
      });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) {
      setDatasetDetail(null);
      setSelectedQueryId('');
      return;
    }

    api.getDataset(selectedDatasetId)
      .then((detail) => {
        setDatasetDetail(detail);
        if (detail.queries.length > 0) {
          setSelectedQueryId(detail.queries[0].query_id);
        }
      })
      .catch((error) => {
        console.error('Error loading dataset detail:', error);
      });
  }, [selectedDatasetId]);

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const loadConversation = async (id: number) => {
    try {
      const data = await api.getConversation(id);
      setMessages(data.messages);
      setActiveConversationId(id);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setLastResponse(null);
  };

  const buildAssistantContent = (searchResponse: SearchResponse) => {
    let assistantContent = '';

    if (searchResponse.answer) {
      assistantContent = searchResponse.answer;
      if (searchResponse.results.length > 0) {
        assistantContent += '\n\nFontes:\n';
        searchResponse.results.slice(0, 3).forEach((result, index) => {
          assistantContent += `**${index + 1}.** ${result.text}\n(Relevancia: ${(result.score * 100).toFixed(1)}%)\n\n`;
        });
      }
    } else if (searchResponse.results.length > 0) {
      assistantContent = `Encontrei ${searchResponse.results.length} resultado(s) relevante(s):\n\n`;
      searchResponse.results.forEach((result, index) => {
        assistantContent += `**${index + 1}.** ${result.text}\n(Relevancia: ${(result.score * 100).toFixed(1)}%)\n\n`;
      });
    } else {
      assistantContent = 'Nao encontrei resultados relevantes para sua busca. Tente reformular sua pergunta ou anexar um documento para analise.';
    }

    if (searchResponse.comparison) {
      const classical = searchResponse.comparison.classical.metrics;
      const quantum = searchResponse.comparison.quantum.metrics;
      if (classical && quantum && classical.has_labels) {
        assistantContent += '\nResumo de comparacao (metrics):\n';
        assistantContent += `Classico - Recall@${classical.k}: ${(classical.recall_at_k ?? 0) * 100}% | MRR: ${(classical.mrr ?? 0) * 100}%\n`;
        assistantContent += `Quantico - Recall@${quantum.k}: ${(quantum.recall_at_k ?? 0) * 100}% | MRR: ${(quantum.mrr ?? 0) * 100}%\n`;
      }
    }

    return assistantContent;
  };

  const handleSendMessage = async (content: string, file?: File) => {
    if (!content.trim() && !file && source !== 'dataset') return;

    setIsLoading(true);

    try {
      let conversationId = activeConversationId;

      const datasetQueryText = datasetDetail?.queries.find((query) => query.query_id === selectedQueryId)?.query;
      const effectiveQuery = source === 'dataset' ? (datasetQueryText ?? content) : content;

      if (source === 'dataset' && !selectedDatasetId) {
        throw new Error('Selecione um dataset para continuar.');
      }

      if (source === 'dataset' && !selectedQueryId) {
        throw new Error('Selecione uma consulta do dataset.');
      }

      // Create new conversation if needed
      if (!conversationId) {
        const title = effectiveQuery.slice(0, 50) + (effectiveQuery.length > 50 ? '...' : '');
        const newConversation = await api.createConversation(title);
        conversationId = newConversation.id;
        setActiveConversationId(conversationId);
        setConversations(prev => [newConversation, ...prev]);
      }

      // Add user message
      const userMessage = await api.addMessage(conversationId, 'user', effectiveQuery);
      setMessages(prev => [...prev, userMessage]);

      let searchResponse: SearchResponse;
      const options = { mode };

      if (source === 'dataset') {
        searchResponse = await api.searchDataset(selectedDatasetId, selectedQueryId, options);
      } else if (file) {
        searchResponse = await api.searchWithFile(effectiveQuery, file, options);
      } else {
        searchResponse = await api.search(effectiveQuery, [], options);
      }

      setLastResponse(searchResponse);

      const assistantContent = buildAssistantContent(searchResponse);

      // Add assistant message
      const assistantMessage = await api.addMessage(conversationId, 'assistant', assistantContent);
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="typing-indicator">
          <span />
          <span />
          <span />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={loadConversation}
        onNewConversation={handleNewConversation}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 flex items-center px-4 border-b border-border">
          {isSidebarCollapsed && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarCollapsed(false)}
              className="mr-2"
            >
              <Menu className="h-5 w-5" />
            </Button>
          )}
          <h1 className="text-lg font-medium">Quantum Search</h1>
        </header>

        {/* Controls */}
        <section className="border-b border-border bg-background/80">
          <div className="max-w-3xl mx-auto px-4 py-4 grid gap-3 md:grid-cols-2">
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Fonte</label>
              <select
                value={source}
                onChange={(event) => setSource(event.target.value as 'file' | 'dataset')}
                className="w-full rounded-lg bg-muted border border-border px-3 py-2 text-sm"
              >
                <option value="file">PDF/TXT</option>
                <option value="dataset">Dataset publico</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Modo</label>
              <select
                value={mode}
                onChange={(event) => setMode(event.target.value as 'classical' | 'quantum' | 'compare')}
                className="w-full rounded-lg bg-muted border border-border px-3 py-2 text-sm"
              >
                <option value="classical">Classico</option>
                <option value="quantum">Quantico</option>
                <option value="compare">Comparar</option>
              </select>
            </div>
          </div>

          {source === 'dataset' && (
            <div className="max-w-3xl mx-auto px-4 pb-4 grid gap-3 md:grid-cols-2">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Dataset</label>
                <select
                  value={selectedDatasetId}
                  onChange={(event) => setSelectedDatasetId(event.target.value)}
                  className="w-full rounded-lg bg-muted border border-border px-3 py-2 text-sm"
                >
                  <option value="">Selecione</option>
                  {datasets.map((dataset) => (
                    <option key={dataset.dataset_id} value={dataset.dataset_id}>
                      {dataset.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Consulta</label>
                <select
                  value={selectedQueryId}
                  onChange={(event) => setSelectedQueryId(event.target.value)}
                  className="w-full rounded-lg bg-muted border border-border px-3 py-2 text-sm"
                >
                  <option value="">Selecione</option>
                  {datasetDetail?.queries.map((query) => (
                    <option key={query.query_id} value={query.query_id}>
                      {query.query}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </section>

        {/* Messages or Welcome */}
        {messages.length === 0 && !isLoading ? (
          <WelcomeScreen />
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}

        {/* Comparison Panel */}
        <ComparisonPanel response={lastResponse} />

        {/* Input */}
        <div className="pb-6 pt-2">
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            allowFile={source === 'file'}
            allowEmptyMessage={source === 'dataset'}
            placeholder={source === 'dataset' ? 'Selecione uma consulta do dataset acima' : 'Pergunte alguma coisa'}
          />
        </div>
      </main>
    </div>
  );
}

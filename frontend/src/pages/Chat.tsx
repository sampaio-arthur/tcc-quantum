import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList } from '@/components/chat/MessageList';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { ComparisonPanel } from '@/components/chat/ComparisonPanel';
import { PipelinePanel } from '@/components/chat/PipelinePanel';
import { useAuth } from '@/contexts/AuthContext';
import { api, Conversation, Message, SearchResponse } from '@/lib/api';

const DEFAULT_DATASET_ID = 'reuters';

export default function Chat() {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const [lastResponse, setLastResponse] = useState<SearchResponse | null>(null);

  const responseCacheKey = (id: number) => `qs:lastResponse:v2:${id}`;

  const loadCachedResponse = (id: number): SearchResponse | null => {
    const raw = localStorage.getItem(responseCacheKey(id));
    if (!raw) return null;
    try {
      return JSON.parse(raw) as SearchResponse;
    } catch {
      localStorage.removeItem(responseCacheKey(id));
      return null;
    }
  };

  const saveCachedResponse = (id: number, response: SearchResponse) => {
    localStorage.setItem(responseCacheKey(id), JSON.stringify(response));
  };

  const clearCachedResponse = (id: number) => {
    localStorage.removeItem(responseCacheKey(id));
  };

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth');
    }
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

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
      setLastResponse(loadCachedResponse(id));
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setLastResponse(null);
  };

  const handleDeleteConversation = async (id: number) => {
    try {
      await api.deleteConversation(id);
      clearCachedResponse(id);
      setConversations((prev) => prev.filter((item) => item.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(null);
        setMessages([]);
        setLastResponse(null);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const buildAssistantContent = (searchResponse: SearchResponse) => {
    const comparison = searchResponse.comparison;
    const classicalResults = comparison?.classical.results ?? searchResponse.results ?? [];
    const quantumResults = comparison?.quantum.results ?? [];
    const comparative = searchResponse.comparison_metrics;
    const classicalLatency = comparison?.classical.metrics?.latency_ms;
    const quantumLatency = comparison?.quantum.metrics?.latency_ms;

    if (!classicalResults.length && !quantumResults.length) {
      return 'Consulta executada, mas nenhum documento foi recuperado.';
    }

    const lines: string[] = [
      `Busca semantica no dataset Reuters (${searchResponse.mode}).`,
    ];

    if (classicalResults.length) {
      lines.push(
        'Classico: ' +
          classicalResults.length +
          ' docs recuperados | melhor score=' +
          classicalResults[0].score.toFixed(3)
      );
    }

    if (quantumResults.length) {
      lines.push(
        'Quantico: ' +
          quantumResults.length +
          ' docs recuperados | melhor score=' +
          quantumResults[0].score.toFixed(3)
      );
    }

    if (classicalLatency !== undefined && quantumLatency !== undefined) {
      lines.push(`Latencia (ms): classico=${classicalLatency.toFixed(1)} | quantico=${quantumLatency.toFixed(1)}`);
    }

    return lines.join('\n');
  };
  const handleSendMessage = async (payload: { message: string }) => {
    const userText = payload.message.trim();
    if (!userText) return;

    setIsLoading(true);

    try {
      let conversationId = activeConversationId;

      if (!conversationId) {
        const title = userText || 'Nova consulta';
        const newConversation = await api.createConversation(title);
        conversationId = newConversation.id;
        setActiveConversationId(conversationId);
        setConversations((prev) => [newConversation, ...prev]);
      }

      const userMessage = await api.addMessage(conversationId, 'user', userText || 'Consulta');
      setMessages((prev) => [...prev, userMessage]);

      await api.indexDataset(DEFAULT_DATASET_ID);
      const searchResponse = await api.searchDataset(userText, DEFAULT_DATASET_ID);

      setLastResponse(searchResponse);
      if (conversationId) {
        saveCachedResponse(conversationId, searchResponse);
      }

      const assistantContent = buildAssistantContent(searchResponse);

      const assistantMessage = await api.addMessage(conversationId, 'assistant', assistantContent);
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const detail = error instanceof Error ? error.message : 'Erro desconhecido';
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: `Nao foi possivel consultar o dataset. ${detail}`,
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
      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={loadConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      <main className="flex-1 flex flex-col min-w-0 min-h-0">
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

        <div className="flex-1 min-h-0 overflow-y-auto">
          {messages.length === 0 && !isLoading ? (
            <WelcomeScreen />
          ) : (
            <MessageList messages={messages} isLoading={isLoading} />
          )}

          <PipelinePanel response={lastResponse} />
          <ComparisonPanel response={lastResponse} />
        </div>

        <div className="pb-6 pt-2">
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}





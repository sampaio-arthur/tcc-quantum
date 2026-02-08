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

export default function Chat() {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

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

  const handleDeleteConversation = async (id: number) => {
    try {
      await api.deleteConversation(id);
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
    let assistantContent = '';

    if (searchResponse.results.length > 0) {
      assistantContent += 'Resultados:\n';
      searchResponse.results.slice(0, 3).forEach((result, index) => {
        assistantContent += `**${index + 1}.** ${result.text}\n(Relevancia: ${(result.score * 100).toFixed(1)}%)\n\n`;
      });
    } else {
      assistantContent = 'Nao encontrei resultados relevantes para sua busca.';
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

    return assistantContent.trim();
  };

  const handleSendMessage = async (filename: string, file: File) => {
    setIsLoading(true);

    try {
      let conversationId = activeConversationId;

      if (!conversationId) {
        const newConversation = await api.createConversation(filename);
        conversationId = newConversation.id;
        setActiveConversationId(conversationId);
        setConversations(prev => [newConversation, ...prev]);
      }

      const userMessage = await api.addMessage(conversationId, 'user', filename);
      setMessages(prev => [...prev, userMessage]);

      const searchResponse = await api.searchWithFile(filename, file, { mode: 'compare' });

      setLastResponse(searchResponse);

      const assistantContent = buildAssistantContent(searchResponse);

      if (assistantContent.length > 0) {
        const assistantMessage = await api.addMessage(conversationId, 'assistant', assistantContent);
        setMessages(prev => [...prev, assistantMessage]);
      }
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
        onDeleteConversation={handleDeleteConversation}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 min-h-0">
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

        <div className="flex-1 min-h-0 overflow-y-auto">
          {/* Messages or Welcome */}
          {messages.length === 0 && !isLoading ? (
            <WelcomeScreen />
          ) : (
            <MessageList messages={messages} isLoading={isLoading} />
          )}

          {/* Pipeline */}
          <PipelinePanel visible={Boolean(lastResponse)} />

          {/* Comparison Panel */}
          <ComparisonPanel response={lastResponse} />
        </div>

        {/* Input */}
        <div className="pb-6 pt-2">
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </main>
    </div>
  );
}

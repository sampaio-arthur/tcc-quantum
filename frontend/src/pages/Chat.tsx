import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageList } from '@/components/chat/MessageList';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { useAuth } from '@/contexts/AuthContext';
import { api, Conversation, Message } from '@/lib/api';
import { cn } from '@/lib/utils';

export default function Chat() {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

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
  };

  const handleSendMessage = async (content: string, file?: File) => {
    if (!content.trim() && !file) return;

    setIsLoading(true);

    try {
      let conversationId = activeConversationId;

      // Create new conversation if needed
      if (!conversationId) {
        const title = content.slice(0, 50) + (content.length > 50 ? '...' : '');
        const newConversation = await api.createConversation(title);
        conversationId = newConversation.id;
        setActiveConversationId(conversationId);
        setConversations(prev => [newConversation, ...prev]);
      }

      // Add user message
      const userMessage = await api.addMessage(conversationId, 'user', content);
      setMessages(prev => [...prev, userMessage]);

      // If file is attached, do search
      let searchResponse;
      if (file) {
        searchResponse = await api.searchWithFile(content, file);
      } else {
        // For demo, just echo back or use search endpoint
        searchResponse = await api.search(content, []);
      }

      // Generate assistant response based on search results
      let assistantContent = '';
      if (searchResponse.results.length > 0) {
        assistantContent = `Encontrei ${searchResponse.results.length} resultado(s) relevante(s):\n\n`;
        searchResponse.results.forEach((result, index) => {
          assistantContent += `**${index + 1}.** ${result.text}\n(Relevância: ${(result.score * 100).toFixed(1)}%)\n\n`;
        });
      } else {
        assistantContent = 'Não encontrei resultados relevantes para sua busca. Tente reformular sua pergunta ou anexar um documento para análise.';
      }

      // Add assistant message
      const assistantMessage = await api.addMessage(conversationId, 'assistant', assistantContent);
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
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

        {/* Messages or Welcome */}
        {messages.length === 0 && !isLoading ? (
          <WelcomeScreen />
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}

        {/* Input */}
        <div className="pb-6 pt-2">
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}

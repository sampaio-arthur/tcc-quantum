import { useRef, useState, type ChangeEvent, type KeyboardEvent } from 'react';
import { Paperclip, ArrowUp, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SendPayload {
  message: string;
  file?: File | null;
}

interface ChatInputProps {
  onSendMessage: (payload: SendPayload) => Promise<void> | void;
  isLoading?: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async () => {
    const trimmed = message.trim();
    if (isLoading) return;
    if (!trimmed && !attachedFile) return;

    const payload: SendPayload = {
      message: trimmed || attachedFile?.name || '',
      file: attachedFile,
    };

    setMessage('');
    setAttachedFile(null);
    await onSendMessage(payload);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['text/plain', 'application/pdf'];
      if (validTypes.includes(file.type)) {
        setAttachedFile(file);
      } else {
        alert('Apenas arquivos TXT e PDF sao permitidos');
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = () => {
    setAttachedFile(null);
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      {attachedFile && (
        <div className="mb-2 flex items-center gap-2 p-2 bg-muted rounded-lg w-fit fade-in">
          <FileText className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-foreground">{attachedFile.name}</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5"
            onClick={removeFile}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      )}

      <div className="chat-input-container flex items-center gap-2 p-3">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground hover:text-foreground flex-shrink-0"
          onClick={() => fileInputRef.current?.click()}
        >
          <Paperclip className="h-5 w-5" />
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              void handleSubmit();
            }
          }}
          placeholder="Digite sua pergunta ou anexe um PDF/TXT"
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
        />

        <Button
          onClick={handleSubmit}
          disabled={(!message.trim() && !attachedFile) || isLoading}
          size="icon"
          className={cn(
            'h-9 w-9 rounded-full flex-shrink-0 transition-colors',
            message.trim() || attachedFile
              ? 'bg-foreground text-background hover:bg-foreground/90'
              : 'bg-muted text-muted-foreground'
          )}
        >
          <ArrowUp className="h-5 w-5" />
        </Button>
      </div>

      <p className="text-xs text-muted-foreground text-center mt-2">
        A comparacao prioriza acuracia; latencia e metrica auxiliar.
      </p>
    </div>
  );
}


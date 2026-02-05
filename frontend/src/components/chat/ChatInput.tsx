import { useState, useRef, KeyboardEvent } from 'react';
import { Paperclip, ArrowUp, X, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string, file?: File) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSendMessage, isLoading, placeholder = 'Pergunte alguma coisa' }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!message.trim() && !attachedFile) return;
    onSendMessage(message, attachedFile || undefined);
    setMessage('');
    setAttachedFile(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['text/plain', 'application/pdf'];
      if (validTypes.includes(file.type)) {
        setAttachedFile(file);
      } else {
        alert('Apenas arquivos TXT e PDF são permitidos');
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = () => {
    setAttachedFile(null);
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto-resize
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      {/* Attached File Preview */}
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

      {/* Input Container */}
      <div className="chat-input-container flex items-end gap-2 p-3">
        {/* Attach Button */}
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

        {/* Text Input */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          className="flex-1 bg-transparent text-foreground placeholder:text-muted-foreground resize-none outline-none py-2 text-sm max-h-[200px]"
          disabled={isLoading}
        />

        {/* Send Button */}
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
        Quantum Search pode cometer erros. Verifique informações importantes.
      </p>
    </div>
  );
}

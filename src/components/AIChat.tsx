import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { queryDeepSeekAI } from '@/lib/openrouter';
import { supabase } from '@/lib/supabase';
import { toast } from 'sonner';
import {
  Send,
  Bot,
  User,
  TrendingUp,
  AlertTriangle,
  FileSearch,
  BarChart3,
  Loader2 } from
'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const AIChat: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userFiles, setUserFiles] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadUserFiles();
    // Add welcome message
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: `Hello ${user?.name}! I'm InsightIQ, your AI business analyst. I can help you analyze your data, generate insights, and answer questions about your uploaded files. How can I assist you today?`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadUserFiles = async () => {
    try {
      const { data, error } = await supabase.
      from('file_uploads').
      select('*').
      eq('user_id', user?.user_id).
      order('upload_timestamp', { ascending: false });

      if (error) {
        console.error('Error loading files:', error);
        return;
      }

      setUserFiles(data || []);
    } catch (error) {
      console.error('Error loading user files:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare context about user's files
      const fileContext = userFiles.
      filter((f) => f.analysis_results).
      map((f) => ({
        name: f.file_name,
        analysis: f.analysis_results
      }));

      const contextMessage = fileContext.length > 0 ?
      `\n\nContext: The user has uploaded ${fileContext.length} files with analysis results: ${fileContext.map((f) => f.name).join(', ')}` :
      '\n\nContext: The user has not uploaded any analyzed files yet.';

      const aiResponse = await queryDeepSeekAI([
      {
        role: 'system',
        content: `You are InsightIQ, an expert business intelligence analyst. You help users understand their data, provide insights, and suggest improvements. Be conversational, helpful, and provide actionable advice. Reference the user's specific files when relevant.${contextMessage}`
      },
      ...messages.slice(-5), // Keep last 5 messages for context
      userMessage]
      );

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI chat error:', error);
      toast.error('Failed to get AI response. Please try again.');

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try asking your question again.',
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePredefinedPrompt = (prompt: string) => {
    setInputValue(prompt);
  };

  const predefinedPrompts = [
  "Summarize key trends in my data",
  "Flag any data quality issues",
  "Suggest validation rules for my datasets",
  "Generate insights from my latest upload",
  "Recommend data visualization strategies",
  "Explain my data dictionary"];


  return (
    <div className="p-6 h-full flex flex-col space-y-6" data-id="c0fn6zzbb" data-path="src/components/AIChat.tsx">
      <div data-id="sdtjde1im" data-path="src/components/AIChat.tsx">
        <h1 className="text-3xl font-bold flex items-center space-x-2" data-id="qealwikeg" data-path="src/components/AIChat.tsx">
          <Bot className="w-8 h-8" data-id="hmry1y61f" data-path="src/components/AIChat.tsx" />
          <span data-id="8clvalg5c" data-path="src/components/AIChat.tsx">InsightIQ AI Assistant</span>
        </h1>
        <p className="text-muted-foreground mt-1" data-id="426y5yhv0" data-path="src/components/AIChat.tsx">
          Your intelligent business analyst - ask questions about your data
        </p>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2" data-id="94votbiql" data-path="src/components/AIChat.tsx">
        {predefinedPrompts.map((prompt, index) =>
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => handlePredefinedPrompt(prompt)}
          disabled={isLoading} data-id="23cqt88z1" data-path="src/components/AIChat.tsx">

            {prompt}
          </Button>
        )}
      </div>

      {/* File Context */}
      {userFiles.length > 0 &&
      <Card data-id="izgil6bnz" data-path="src/components/AIChat.tsx">
          <CardHeader data-id="o3xx4f5d6" data-path="src/components/AIChat.tsx">
            <CardTitle className="text-sm flex items-center space-x-2" data-id="nukjp9mvt" data-path="src/components/AIChat.tsx">
              <FileSearch className="w-4 h-4" data-id="hzno73gmj" data-path="src/components/AIChat.tsx" />
              <span data-id="wnz3056k7" data-path="src/components/AIChat.tsx">Available Data ({userFiles.length} files)</span>
            </CardTitle>
          </CardHeader>
          <CardContent data-id="sugxfk2qq" data-path="src/components/AIChat.tsx">
            <div className="flex flex-wrap gap-2" data-id="f5avcf37n" data-path="src/components/AIChat.tsx">
              {userFiles.slice(0, 5).map((file) =>
            <Badge key={file.id} variant={file.analysis_results ? 'default' : 'secondary'} data-id="r8x5x5t8c" data-path="src/components/AIChat.tsx">
                  {file.file_name}
                  {file.analysis_results && <BarChart3 className="w-3 h-3 ml-1" data-id="k7d1mvzyg" data-path="src/components/AIChat.tsx" />}
                </Badge>
            )}
              {userFiles.length > 5 &&
            <Badge variant="outline" data-id="xf3sc9xal" data-path="src/components/AIChat.tsx">+{userFiles.length - 5} more</Badge>
            }
            </div>
          </CardContent>
        </Card>
      }

      {/* Chat Messages */}
      <Card className="flex-1 flex flex-col" data-id="uyt0w4rtr" data-path="src/components/AIChat.tsx">
        <CardContent className="p-0 flex-1 flex flex-col" data-id="o554dc2ek" data-path="src/components/AIChat.tsx">
          <ScrollArea className="flex-1 p-4" data-id="6mhu31sgr" data-path="src/components/AIChat.tsx">
            <div className="space-y-4" data-id="jdl1aezti" data-path="src/components/AIChat.tsx">
              {messages.map((message) =>
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'}`
                } data-id="hsejgrqds" data-path="src/components/AIChat.tsx">

                  {message.role === 'assistant' &&
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center" data-id="v1dd4kfgw" data-path="src/components/AIChat.tsx">
                      <Bot className="w-4 h-4 text-primary" data-id="oezf8x9nf" data-path="src/components/AIChat.tsx" />
                    </div>
                }
                  
                  <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user' ?
                  'bg-primary text-primary-foreground' :
                  'bg-muted'}`
                  } data-id="az5w9rrtr" data-path="src/components/AIChat.tsx">

                    <div className="whitespace-pre-wrap text-sm" data-id="1sh48d85t" data-path="src/components/AIChat.tsx">{message.content}</div>
                    <div className={`text-xs mt-2 opacity-70`} data-id="8twtebc0o" data-path="src/components/AIChat.tsx">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>

                  {message.role === 'user' &&
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center" data-id="rb13wtpl1" data-path="src/components/AIChat.tsx">
                      <User className="w-4 h-4 text-primary-foreground" data-id="gbxv46w0k" data-path="src/components/AIChat.tsx" />
                    </div>
                }
                </div>
              )}
              
              {isLoading &&
              <div className="flex items-start space-x-3" data-id="8zzfonkfr" data-path="src/components/AIChat.tsx">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center" data-id="vehre1uii" data-path="src/components/AIChat.tsx">
                    <Bot className="w-4 h-4 text-primary" data-id="qpk9ezty4" data-path="src/components/AIChat.tsx" />
                  </div>
                  <div className="bg-muted rounded-lg p-3" data-id="3wqy143c9" data-path="src/components/AIChat.tsx">
                    <div className="flex items-center space-x-2 text-sm" data-id="vd37x06l7" data-path="src/components/AIChat.tsx">
                      <Loader2 className="w-4 h-4 animate-spin" data-id="lfm25s8be" data-path="src/components/AIChat.tsx" />
                      <span data-id="336b67oz3" data-path="src/components/AIChat.tsx">InsightIQ is thinking...</span>
                    </div>
                  </div>
                </div>
              }
              
              <div ref={messagesEndRef} data-id="kc577vtsm" data-path="src/components/AIChat.tsx" />
            </div>
          </ScrollArea>

          {/* Input Form */}
          <div className="border-t p-4" data-id="mja4p9xbo" data-path="src/components/AIChat.tsx">
            <form onSubmit={handleSubmit} className="flex space-x-2" data-id="azg1qefom" data-path="src/components/AIChat.tsx">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask InsightIQ about your data..."
                disabled={isLoading}
                className="flex-1" data-id="xo3irbaln" data-path="src/components/AIChat.tsx" />

              <Button type="submit" disabled={isLoading || !inputValue.trim()} data-id="9eq9pievv" data-path="src/components/AIChat.tsx">
                {isLoading ?
                <Loader2 className="w-4 h-4 animate-spin" data-id="9tob5pp3d" data-path="src/components/AIChat.tsx" /> :

                <Send className="w-4 h-4" data-id="6vtoamu28" data-path="src/components/AIChat.tsx" />
                }
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>);

};

export default AIChat;
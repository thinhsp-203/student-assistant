import { Message, Source } from '../types';

export const chatService = {
  streamChatResponse: async (
    message: string,
    history: Message[],
    studentId: string,
    topic: string,
    signal: AbortSignal,
    onChunk: (text: string) => void,
    onSources: (sources: Source[]) => void,
    onDone: () => void,
    onError: (error: Error) => void
  ) => {
    try {
      const response = await fetch('/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          student_id: studentId,
          topic_mode: topic,
          history: history.map(msg => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        
        if (done) {
          onDone();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop() || ''; // Keep the incomplete line in the buffer

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || !trimmedLine.startsWith('data: ')) continue;
          
          const data = trimmedLine.slice(6);
          
          if (data === '[DONE]') {
            continue;
          }

          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              onError(new Error(parsed.error));
            } else {
              if (parsed.answer) {
                onChunk(parsed.answer);
              }
              if (parsed.sources && parsed.sources.length > 0) {
                onSources(parsed.sources);
              }
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, 'Data:', data);
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Stream aborted');
        onDone();
      } else {
        onError(error);
      }
    }
  }
};

// components/chat/ChatInput.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { Paperclip, Mic, Send, Globe, Book } from "lucide-react";

export default function ChatInput({ onSend }: { onSend: (text: string) => void }) {
  const [value, setValue] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const win: any = window;
    const SpeechRecognition = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const r = new SpeechRecognition();
    r.lang = "en-US";
    r.interimResults = false;
    r.maxAlternatives = 1;
    recognitionRef.current = r;
    r.onresult = (ev: any) => {
      const t = ev.results[0][0].transcript;
      setValue((v) => (v ? v + " " + t : t));
    };
    r.onend = () => setListening(false);
  }, []);

  const toggleListen = () => {
    if (!recognitionRef.current) return alert("Speech Recognition not supported in this browser.");
    if (!listening) {
      recognitionRef.current.start();
      setListening(true);
    } else {
      recognitionRef.current.stop();
      setListening(false);
    }
  };

  const submit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!value.trim()) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <form onSubmit={(e) => submit(e)} className="border-t border-border bg-background p-4 flex items-center gap-3 flex-shrink-0">
      <button 
        type="button" 
        className="text-muted-foreground p-2 rounded-lg hover:bg-accent hover:text-accent-foreground transition-colors" 
        onClick={() => alert("Attach (mock)")}
        title="Attach file"
      >
        <Paperclip size={18} />
      </button>

      <div className="flex items-center gap-2 bg-secondary border border-border rounded-lg px-4 py-2.5 flex-1 focus-within:ring-2 focus-within:ring-ring/20">
        <input
          className="flex-1 bg-transparent text-foreground text-sm outline-none placeholder:text-muted-foreground"
          placeholder="Ask anything..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <div className="flex items-center gap-1">
          <button 
            type="button" 
            className="p-1.5 rounded-md hover:bg-accent text-muted-foreground hover:text-accent-foreground transition-colors" 
            onClick={() => alert("Search (mock)")}
            title="Search web"
          >
            <Globe size={16} />
          </button>
          <button 
            type="button" 
            className="p-1.5 rounded-md hover:bg-accent text-muted-foreground hover:text-accent-foreground transition-colors" 
            onClick={() => alert("Study mode (mock)")}
            title="Study mode"
          >
            <Book size={16} />
          </button>
        </div>
      </div>

      <button 
        type="button" 
        className={`p-2 rounded-lg transition-colors ${listening ? "bg-rose-500 text-white hover:bg-rose-600" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"}`} 
        onClick={toggleListen}
        title="Voice input"
      >
        <Mic size={18} />
      </button>

      <button 
        type="submit" 
        className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
        disabled={!value.trim()}
      >
        <Send size={16} />
        <span className="text-sm font-medium">Send</span>
      </button>
    </form>
  );
}

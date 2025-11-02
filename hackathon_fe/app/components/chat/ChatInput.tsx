// components/chat/ChatInput.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { Paperclip, Mic, Send, Globe, Book } from "lucide-react";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
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
    <form onSubmit={(e) => submit(e)} className="border-t border-blue-900/20 bg-[#0a0e13] p-5 flex items-center gap-3 shrink-0 shadow-2xl">
      <button 
        type="button" 
        className="text-gray-400 p-2.5 rounded-xl hover:bg-blue-900/20 hover:text-white transition-all disabled:opacity-50 border border-transparent hover:border-blue-500/30" 
        onClick={() => alert("Attach (mock)")}
        title="Attach file"
        disabled={disabled}
      >
        <Paperclip size={20} />
      </button>

      <div className="flex items-center gap-2 bg-[#1a1f2e] border border-blue-900/30 rounded-2xl px-5 py-3 flex-1 focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500/50 transition-all shadow-lg">
        <input
          className="flex-1 bg-transparent text-white text-sm outline-none placeholder:text-gray-500 disabled:cursor-not-allowed"
          placeholder={disabled ? "⏳ Chờ kết nối WebSocket..." : "💬 Nhập tin nhắn..."}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
        />
        <div className="flex items-center gap-1">
          <button 
            type="button" 
            className="p-2 rounded-lg hover:bg-blue-900/20 text-gray-400 hover:text-blue-400 transition-all disabled:opacity-50 border border-transparent hover:border-blue-500/20" 
            onClick={() => alert("Search (mock)")}
            title="Search web"
            disabled={disabled}
          >
            <Globe size={16} />
          </button>
          <button 
            type="button" 
            className="p-2 rounded-lg hover:bg-blue-900/20 text-gray-400 hover:text-blue-400 transition-all disabled:opacity-50 border border-transparent hover:border-blue-500/20" 
            onClick={() => alert("Study mode (mock)")}
            title="Study mode"
            disabled={disabled}
          >
            <Book size={16} />
          </button>
        </div>
      </div>

      <button 
        type="button" 
        className={`p-2.5 rounded-xl transition-all disabled:opacity-50 border ${
          listening 
            ? "bg-red-500 text-white hover:bg-red-600 border-red-500/30 shadow-lg shadow-red-500/20" 
            : "text-gray-400 hover:text-white hover:bg-blue-900/20 border-transparent hover:border-blue-500/30"
        }`} 
        onClick={toggleListen}
        title="Voice input"
        disabled={disabled}
      >
        <Mic size={20} />
      </button>

      <button 
        type="submit" 
        className="bg-linear-to-r from-blue-600 to-blue-500 text-white px-6 py-3 rounded-xl hover:from-blue-500 hover:to-blue-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-lg shadow-blue-500/20 border border-blue-400/30"
        disabled={!value.trim() || disabled}
      >
        <Send size={18} />
        <span>Send</span>
      </button>
    </form>
  );
}

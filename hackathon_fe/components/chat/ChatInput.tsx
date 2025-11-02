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
    <form onSubmit={(e) => submit(e)} className="border-t border-gray-800 bg-[#111214] p-4 flex items-center gap-3">
      <button type="button" className="text-neutral-300 p-2 rounded-md hover:bg-[#2a2b32]" onClick={() => alert("Attach (mock)")}>
        <Paperclip size={18} />
      </button>

      <div className="flex items-center gap-2 bg-neutral-800/40 rounded-full px-3 py-2 flex-1">
        <input
          className="flex-1 bg-transparent text-neutral-100 text-sm outline-none placeholder:text-neutral-400"
          placeholder="Ask anything..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <div className="flex items-center gap-2">
          <button type="button" className="px-2 py-1 rounded-md hover:bg-neutral-700/40 text-neutral-300" onClick={() => alert("Search (mock)")}>
            <Globe size={16} />
            <span className="sr-only">Search</span>
          </button>
          <button type="button" className="px-2 py-1 rounded-md hover:bg-neutral-700/40 text-neutral-300" onClick={() => alert("Study mode (mock)")}>
            <Book size={16} />
            <span className="sr-only">Study</span>
          </button>
        </div>
      </div>

      <button type="button" className={`p-2 rounded-md ${listening ? "bg-rose-600 text-white" : "hover:bg-neutral-700/40 text-neutral-300"}`} onClick={toggleListen}>
        <Mic size={18} />
      </button>

      <button type="submit" className="bg-[#10a37f] text-white px-3 py-2 rounded-md hover:bg-[#0e8f6d]">
        <Send size={16} />
      </button>
    </form>
  );
}

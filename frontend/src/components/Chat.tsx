import { useState, useRef, useEffect } from "react"
import { useBackend } from "../hooks/useBackend"

interface Message {
  role: "user" | "agent"
  text: string
}

export default function Chat() {
  const { send, status } = useBackend()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || status !== "connected") return
    const userMsg = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", text: userMsg }])

    try {
      const result = await send("echo", { text: userMsg }) as string
      setMessages((prev) => [...prev, { role: "agent", text: String(result) }])
    } catch {
      setMessages((prev) => [...prev, { role: "agent", text: "Error: Could not reach backend" }])
    }
  }

  return (
    <div className="flex-1 flex flex-col" style={{ background: "var(--bg-primary)" }}>
      <div className="text-sm font-medium px-4 py-2 border-b" style={{ borderColor: "var(--border)", color: "var(--accent-2)" }}>
        💬 Chat
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center mt-20" style={{ color: "var(--text-secondary)" }}>
            <div className="text-3xl mb-3">🧠</div>
            <p className="text-sm">Ask Neuro Agent anything</p>
            <p className="text-xs mt-1">Try: "research papers about attention mechanisms"</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] px-3 py-2 rounded-xl text-sm`}
              style={{
                background: m.role === "user" ? "var(--accent)" : "var(--bg-tertiary)",
                color: m.role === "user" ? "#fff" : "var(--text-primary)",
              }}>
              {m.text}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div className="p-3 border-t" style={{ borderColor: "var(--border)" }}>
        <div className="flex gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={status === "connected" ? "Type a message..." : "Connecting..."}
            disabled={status !== "connected"}
            className="flex-1 text-sm px-3 py-2 rounded-lg outline-none"
            style={{ background: "var(--bg-secondary)", color: "var(--text-primary)", border: "1px solid var(--border)" }} />
          <button onClick={handleSend} disabled={status !== "connected"}
            className="px-4 py-2 rounded-lg text-sm font-medium"
            style={{ background: "var(--accent)", color: "#fff" }}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

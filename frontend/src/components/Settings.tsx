import { useState } from "react"
import { themeLabels, type Theme } from "../hooks/useTheme"

interface SettingsProps {
  theme: Theme
  setTheme: (t: Theme) => void
  onClose: () => void
}

const providers = [
  { value: "deepseek", label: "DeepSeek" },
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "mistral", label: "Mistral" },
  { value: "qwen", label: "Qwen" },
  { value: "openrouter", label: "OpenRouter" },
  { value: "ollama", label: "Ollama (local)" },
]

function loadSetting(key: string, fallback: string): string {
  return localStorage.getItem(`neuro-${key}`) || fallback
}

function saveSetting(key: string, value: string) {
  localStorage.setItem(`neuro-${key}`, value)
}

export default function Settings({ theme, setTheme, onClose }: SettingsProps) {
  const [provider, setProvider] = useState(() => loadSetting("provider", "deepseek"))
  const [apiKey, setApiKey] = useState(() => loadSetting("apikey", ""))
  const [model, setModel] = useState(() => loadSetting("model", ""))
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    saveSetting("provider", provider)
    saveSetting("apikey", apiKey)
    saveSetting("model", model)
    try {
      // Send config to backend via WebSocket command
      const ws = new WebSocket(`ws://127.0.0.1:9876/ws/settings`)
      await new Promise<void>((resolve) => {
        ws.onopen = () => {
          ws.send(JSON.stringify({ type: "config", provider, api_key: apiKey, model }))
          ws.onmessage = () => { ws.close(); resolve() }
          setTimeout(() => { ws.close(); resolve() }, 2000)
        }
        ws.onerror = () => { ws.close(); resolve() } // non-blocking
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {
      setSaved(true) // still saved locally
      setTimeout(() => setSaved(false), 2000)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}
      onClick={onClose}>
      <div className="w-96 max-h-[80vh] overflow-y-auto rounded-xl p-5" style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}
        onClick={(e) => e.stopPropagation()}>
        <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-primary)" }}>Settings</h3>

        <div className="mb-4">
          <label className="text-xs mb-1 block" style={{ color: "var(--text-secondary)" }}>LLM Provider</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}
            className="w-full text-xs px-2 py-1.5 rounded-lg outline-none"
            style={{ background: "var(--bg-tertiary)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
            {providers.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>

        <div className="mb-4">
          <label className="text-xs mb-1 block" style={{ color: "var(--text-secondary)" }}>API Key</label>
          <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full text-xs px-2 py-1.5 rounded-lg outline-none"
            style={{ background: "var(--bg-tertiary)", color: "var(--text-primary)", border: "1px solid var(--border)" }} />
        </div>

        <div className="mb-4">
          <label className="text-xs mb-1 block" style={{ color: "var(--text-secondary)" }}>Model (optional, uses default if empty)</label>
          <input value={model} onChange={(e) => setModel(e.target.value)}
            placeholder="e.g. deepseek-v4-pro"
            className="w-full text-xs px-2 py-1.5 rounded-lg outline-none"
            style={{ background: "var(--bg-tertiary)", color: "var(--text-primary)", border: "1px solid var(--border)" }} />
        </div>

        <div className="mb-4">
          <label className="text-xs mb-1 block" style={{ color: "var(--text-secondary)" }}>Theme</label>
          <div className="grid grid-cols-2 gap-2">
            {(Object.keys(themeLabels) as Theme[]).map((t) => (
              <button key={t}
                onClick={() => setTheme(t)}
                className="text-xs px-3 py-2 rounded-lg text-left transition-all"
                style={{
                  background: theme === t ? "var(--accent)" : "var(--bg-tertiary)",
                  color: theme === t ? "#fff" : "var(--text-primary)",
                }}>
                {themeLabels[t]}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <button onClick={handleSave}
            className="flex-1 text-xs py-2 rounded-lg font-medium"
            style={{ background: saved ? "#22c55e" : "var(--accent)", color: "#fff" }}>
            {saved ? "Saved!" : "Save Settings"}
          </button>
          <button onClick={onClose} className="flex-1 text-xs py-2 rounded-lg"
            style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

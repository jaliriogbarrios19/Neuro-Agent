import { themeLabels, type Theme } from "../hooks/useTheme"

interface SettingsProps {
  theme: Theme
  setTheme: (t: Theme) => void
  onClose: () => void
}

export default function Settings({ theme, setTheme, onClose }: SettingsProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}
      onClick={onClose}>
      <div className="w-80 rounded-xl p-5" style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}
        onClick={(e) => e.stopPropagation()}>
        <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-primary)" }}>Theme</h3>
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
        <button onClick={onClose} className="mt-4 text-xs w-full py-2 rounded-lg"
          style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}>
          Close
        </button>
      </div>
    </div>
  )
}

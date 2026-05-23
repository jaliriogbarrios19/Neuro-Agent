import { useState } from "react"
import { useBackend } from "./hooks/useBackend"
import { useTheme } from "./hooks/useTheme"
import Sidebar from "./components/Sidebar"
import FileTree from "./components/FileTree"
import NoteEditor from "./components/NoteEditor"
import SlideEditor from "./components/SlideEditor"
import Settings from "./components/Settings"

type View = "notes" | "slides"

function App() {
  const { status } = useBackend()
  const { theme, setTheme } = useTheme()
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [view, setView] = useState<View>("notes")
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className="flex h-screen w-screen" style={{ background: "var(--bg-primary)" }}>
      <Sidebar status={status} onRefresh={() => window.location.reload()} />
      <FileTree onSelect={(path) => { setSelectedFile(path); setView("notes") }} />
      <div className="flex-1 flex flex-col">
        <div className="flex items-center px-4 py-1.5 border-b gap-3" style={{ borderColor: "var(--border)" }}>
          <button onClick={() => setView("notes")}
            className="text-xs px-3 py-1 rounded-md font-medium"
            style={{ background: view === "notes" ? "var(--accent)" : "var(--bg-tertiary)", color: view === "notes" ? "#fff" : "var(--text-primary)" }}>
            📝 Notes
          </button>
          <button onClick={() => setView("slides")}
            className="text-xs px-3 py-1 rounded-md font-medium"
            style={{ background: view === "slides" ? "var(--accent)" : "var(--bg-tertiary)", color: view === "slides" ? "#fff" : "var(--text-primary)" }}>
            📊 Slides
          </button>
          <div className="flex-1" />
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
            {status === "connected" ? "🟢 Connected" : status === "connecting" ? "🟡 Connecting" : "🔴 Offline"}
          </span>
          <button onClick={() => setShowSettings(true)} className="w-6 h-6 rounded flex items-center justify-center" title="Settings">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
          </button>
        </div>

        {view === "notes" ? (
          <NoteEditor filePath={selectedFile} />
        ) : (
          <SlideEditor />
        )}
      </div>

      {showSettings && (
        <Settings theme={theme} setTheme={setTheme} onClose={() => setShowSettings(false)} />
      )}
    </div>
  )
}

export default App

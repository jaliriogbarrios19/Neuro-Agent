type ViewType = "notes" | "slides" | "chat" | "transcription"

interface SidebarProps {
  status: string
  onRefresh: () => void
  onViewChange: (view: ViewType) => void
  activeView: ViewType
}

export default function Sidebar({ status, onRefresh, onViewChange, activeView }: SidebarProps) {
  const dotColor = status === "connected" ? "bg-green-400" : status === "connecting" ? "bg-yellow-400" : "bg-red-400"

  const btnStyle = (isActive: boolean) => ({
    background: isActive ? "var(--accent)" : "var(--bg-tertiary)" as string,
    color: isActive ? "#fff" : "var(--text-primary)" as string,
  })

  return (
    <aside style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}
      className="w-14 flex flex-col items-center py-4 gap-3 border-r shrink-0">
      <div className="w-9 h-9 rounded-lg flex items-center justify-center font-bold text-sm"
        style={{ background: "var(--accent)", color: "#fff" }}>N</div>

      <nav className="flex flex-col gap-2 mt-4">
        <button title="Notes" onClick={() => onViewChange("notes")}
          className="w-9 h-9 rounded-lg flex items-center justify-center hover:opacity-80 transition-opacity"
          style={btnStyle(activeView === "notes")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </button>
        <button title="Chat" onClick={() => onViewChange("chat")}
          className="w-9 h-9 rounded-lg flex items-center justify-center hover:opacity-80 transition-opacity"
          style={btnStyle(activeView === "chat")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </button>
        <button title="Slides" onClick={() => onViewChange("slides")}
          className="w-9 h-9 rounded-lg flex items-center justify-center hover:opacity-80 transition-opacity"
          style={btnStyle(activeView === "slides")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </button>
        <button title="Transcription" onClick={() => onViewChange("transcription")}
          className="w-9 h-9 rounded-lg flex items-center justify-center hover:opacity-80 transition-opacity"
          style={btnStyle(activeView === "transcription")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
        </button>
      </nav>

      <div className="mt-auto flex flex-col gap-2 items-center">
        <button onClick={onRefresh} title="Refresh" className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: "var(--bg-tertiary)" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
        </button>
        <div className={`w-2 h-2 rounded-full ${dotColor}`} title={status} />
      </div>
    </aside>
  )
}

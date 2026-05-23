import { useState, useEffect } from "react"
import { useBackend } from "../hooks/useBackend"

interface NoteEditorProps {
  filePath: string | null
}

export default function NoteEditor({ filePath }: NoteEditorProps) {
  const { send, status } = useBackend()
  const [content, setContent] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!filePath || status !== "connected") return
    let cancelled = false
    send("read_file", { path: filePath }).then((data) => {
      if (!cancelled) setContent(data as string)
    }).catch(() => {
      if (!cancelled) setContent("")
    })
    return () => { cancelled = true }
  }, [filePath, status, send])

  const handleSave = async () => {
    if (!filePath) return
    setSaving(true)
    await send("write_file", { path: filePath, content })
    setSaving(false)
  }

  if (!filePath) {
    return (
      <div className="flex-1 flex items-center justify-center" style={{ color: "var(--text-secondary)" }}>
        <div className="text-center">
          <div className="text-4xl mb-3">🧠</div>
          <h2 className="text-lg font-semibold mb-1" style={{ color: "var(--text-primary)" }}>Neuro Agent</h2>
          <p className="text-sm">Select a note or start a conversation</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b" style={{ borderColor: "var(--border)" }}>
        <span className="text-sm font-medium" style={{ color: "var(--accent-2)" }}>{filePath}</span>
        <button onClick={handleSave} disabled={saving}
          className="text-xs px-3 py-1 rounded-md font-medium transition-colors"
          style={{ background: "var(--accent)", color: "#fff" }}>
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={(e) => { if (e.ctrlKey && e.key === "s") { e.preventDefault(); handleSave() } }}
        placeholder="Start writing..."
        className="flex-1 w-full resize-none p-4 text-sm leading-relaxed outline-none"
        style={{
          background: "var(--bg-primary)",
          color: "var(--text-primary)",
          fontFamily: "var(--font-mono)",
          border: "none",
        }}
      />
    </div>
  )
}

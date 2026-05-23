import { useState, useEffect } from "react"
import { useBackend } from "../hooks/useBackend"

interface FileEntry {
  name: string
  isDir: boolean
}

export default function FileTree({ onSelect }: { onSelect: (path: string) => void }) {
  const { send, status } = useBackend()
  const [files, setFiles] = useState<FileEntry[]>([])
  const [active, setActive] = useState("")

  useEffect(() => {
    let cancelled = false
    if (status !== "connected") return
    send("list_directory", { path: "." }).then((result) => {
      if (cancelled) return
      setFiles((result as string[]).map((n: string) => ({ name: n, isDir: n.endsWith("/") })))
    }).catch(() => {})
    return () => { cancelled = true }
  }, [status, send])

  return (
    <div className="w-56 border-r shrink-0 py-3 px-2" style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}>
      <div className="text-xs font-semibold uppercase tracking-wider mb-3 px-2" style={{ color: "var(--text-secondary)" }}>Vault</div>
      {files.map((f) => (
        <button
          key={f.name}
          onClick={() => { setActive(f.name); onSelect(f.name) }}
          className="w-full text-left px-3 py-1.5 rounded text-sm flex items-center gap-2"
          style={{
            background: active === f.name ? "var(--bg-tertiary)" : "transparent",
            color: active === f.name ? "var(--accent)" : "var(--text-primary)",
          }}>
          <span>{f.isDir ? "📁" : "📄"}</span>
          <span className="truncate">{f.name}</span>
        </button>
      ))}
      {files.length === 0 && (
        <div className="text-xs px-2" style={{ color: "var(--text-secondary)" }}>No files yet</div>
      )}
    </div>
  )
}

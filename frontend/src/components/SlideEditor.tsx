import { useState, useRef, useEffect, useCallback } from "react"
import SlideToolbar from "./SlideToolbar"

const DEFAULT_SLIDES = `---
marp: true
theme: default
paginate: true
---

# Welcome to Neuro Slides

Your AI-powered presentation builder

---

## How it works

- Write in **Markdown**
- Use the toolbar above for help
- Separate slides with \`---\`
- Export to PDF when ready

---

## Your AI Assistant

Ask Neuro Agent to help you create slides:

> "Create 3 slides about photosynthesis for my biology class"

---

# Thank you! 🧠
`

export default function SlideEditor() {
  const [markdown, setMarkdown] = useState(DEFAULT_SLIDES)
  const [previewHtml, setPreviewHtml] = useState("")
  const [viewMode, setViewMode] = useState<"split" | "preview">("split")
  const [exporting, setExporting] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const workerRef = useRef<Worker | null>(null)

  useEffect(() => {
    workerRef.current = new Worker(
      new URL("../workers/marp.worker.ts", import.meta.url),
      { type: "module" }
    )
    workerRef.current.onmessage = (e) => setPreviewHtml(e.data)
    return () => workerRef.current?.terminate()
  }, [])

  useEffect(() => {
    workerRef.current?.postMessage(markdown)
  }, [markdown])

  const handleInsert = useCallback((text: string) => {
    const ta = textareaRef.current
    if (!ta) return
    const start = ta.selectionStart
    const end = ta.selectionEnd
    const newText = markdown.slice(0, start) + text + markdown.slice(end)
    setMarkdown(newText)
    requestAnimationFrame(() => {
      ta.focus()
      ta.setSelectionRange(start + text.length, start + text.length)
    })
  }, [markdown])

  const handleExport = async () => {
    setExporting(true)
    try {
      const { Marp } = await import("@marp-team/marp-core")
      const marp = new Marp()
      const { html } = marp.render(markdown)
      const blob = new Blob([`<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{margin:0}</style></head><body>${html}</body></html>`], { type: "text/html" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "slides.html"
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col" style={{ background: "var(--bg-primary)" }}>
      <div className="flex items-center justify-between px-4 py-2 border-b" style={{ borderColor: "var(--border)" }}>
        <span className="text-sm font-medium" style={{ color: "var(--accent-2)" }}>📊 Slides</span>
        <div className="flex items-center gap-2">
          <button onClick={() => setViewMode(viewMode === "split" ? "preview" : "split")}
            className="text-xs px-2.5 py-1 rounded-md"
            style={{ background: "var(--bg-tertiary)", color: "var(--text-primary)" }}>
            {viewMode === "split" ? "Preview Only" : "Split View"}
          </button>
          <button onClick={handleExport} disabled={exporting}
            className="text-xs px-3 py-1 rounded-md font-medium"
            style={{ background: "var(--accent)", color: "#fff" }}>
            {exporting ? "Exporting..." : "Export HTML"}
          </button>
        </div>
      </div>

      <SlideToolbar onInsert={handleInsert} />

      <div className="flex-1 flex overflow-hidden">
        {viewMode === "split" && (
          <textarea ref={textareaRef}
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            className="w-1/2 resize-none p-4 text-sm leading-relaxed outline-none border-r"
            style={{
              background: "var(--bg-primary)",
              color: "var(--text-primary)",
              fontFamily: "var(--font-mono)",
              borderColor: "var(--border)",
            }}
            spellCheck={false}
          />
        )}
        <div className={`${viewMode === "split" ? "w-1/2" : "w-full"} overflow-auto`}
          style={{ background: "#fff" }}
          dangerouslySetInnerHTML={{ __html: previewHtml }}
        />
      </div>
    </div>
  )
}

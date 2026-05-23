interface SlideToolbarProps {
  onInsert: (text: string) => void
}

const tools = [
  { label: "Title", insert: "\n# Slide Title\n" },
  { label: "Subtitle", insert: "\n## Subtitle\n" },
  { label: "Bullets", insert: "\n- Point one\n- Point two\n- Point three\n" },
  { label: "Image", insert: '\n![bg right](https://)\n' },
  { label: "Columns", insert: '\n<div class="columns">\n<div>\n\nLeft content\n\n</div>\n<div>\n\nRight content\n\n</div>\n</div>\n' },
  { label: "Code", insert: "\n```python\n# your code here\n```\n" },
  { label: "Quote", insert: "\n> Important quote or insight\n" },
  { label: "New Slide", insert: "\n---\n" },
]

export default function SlideToolbar({ onInsert }: SlideToolbarProps) {
  return (
    <div className="flex gap-1 px-3 py-2 border-b flex-wrap" style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
      {tools.map((t) => (
        <button key={t.label}
          onClick={() => onInsert(t.insert)}
          className="text-xs px-2.5 py-1 rounded-md hover:opacity-80 transition-opacity font-medium"
          style={{ background: "var(--bg-tertiary)", color: "var(--text-primary)" }}>
          {t.label}
        </button>
      ))}
    </div>
  )
}

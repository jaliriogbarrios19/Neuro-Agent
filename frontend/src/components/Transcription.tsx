import { useState } from "react"
import { useBackend } from "../hooks/useBackend"

export default function Transcription() {
  const { send, status } = useBackend()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState("")

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setResult("")
    try {
      const data = await send("transcribe_audio", { file_path: (file as any).path || file.name, language: "es" })
      const text = typeof data === "object" ? (data as any).text || JSON.stringify(data) : String(data)
      setResult(text)
    } catch (err: any) {
      setResult("Error: " + (err.message || "Transcription failed"))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col" style={{ background: "var(--bg-primary)" }}>
      <div className="text-sm font-medium px-4 py-2 border-b" style={{ borderColor: "var(--border)", color: "var(--accent-2)" }}>
        🎙️ Transcription
      </div>
      <div className="flex-1 p-6 flex flex-col items-center justify-center gap-4">
        <div className="text-center">
          <div className="text-4xl mb-3">🎙️</div>
          <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>Transcribe audio files with speaker diarization</p>
        </div>
        <label className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
          style={{ background: "var(--accent)", color: "#fff" }}>
          {loading ? "Transcribing..." : "Select Audio File"}
          <input type="file" accept="audio/*" className="hidden" onChange={handleFile} disabled={loading} />
        </label>
        {status !== "connected" && (
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>Backend not connected</p>
        )}
        {result && (
          <div className="w-full max-w-2xl mt-4 p-4 rounded-lg text-sm" style={{ background: "var(--bg-secondary)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
            <div className="font-medium mb-2" style={{ color: "var(--accent-2)" }}>Transcript:</div>
            <div className="whitespace-pre-wrap">{result}</div>
          </div>
        )}
      </div>
    </div>
  )
}

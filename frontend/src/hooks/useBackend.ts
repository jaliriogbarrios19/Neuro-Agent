import { useState, useEffect, useRef, useCallback } from "react"

type BackendStatus = "connecting" | "connected" | "disconnected" | "error"

interface PendingRequest {
  resolve: (value: unknown) => void
  reject: (reason: Error) => void
}

interface UseBackendResult {
  status: BackendStatus
  sessionId: string | null
  send: (tool: string, args: Record<string, unknown>) => Promise<unknown>
}

export function useBackend(): UseBackendResult {
  const [status, setStatus] = useState<BackendStatus>("connecting")
  const [sessionId, setSessionId] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const pendingRef = useRef<Map<string, PendingRequest>>(new Map())
  const connectRef = useRef<() => void>(null as unknown as () => void)

  const connect = useCallback(() => {
    const id = crypto.randomUUID()
    const ws = new WebSocket(`ws://127.0.0.1:9876/ws/${id}`)

    ws.onopen = () => {}

    ws.onmessage = (event) => {
      let msg: Record<string, unknown>
      try {
        msg = JSON.parse(event.data)
      } catch {
        return
      }

      if (msg.type === "connected") {
        setSessionId(msg.session_id as string)
        setStatus("connected")
      } else if (msg.type === "result") {
        const pending = pendingRef.current.get(msg.id as string)
        if (pending) {
          pendingRef.current.delete(msg.id as string)
          if (msg.ok) {
            pending.resolve(msg.data)
          } else {
            pending.reject(new Error(msg.error as string))
          }
        }
      }
    }

    ws.onclose = () => {
      setStatus("disconnected")
      setTimeout(() => connectRef.current?.(), 1000)
    }

    ws.onerror = () => {
      setStatus("error")
      ws.close()
    }

    wsRef.current = ws
  }, [])

  useEffect(() => {
    connectRef.current = connect
  }, [connect])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback(
    (tool: string, args: Record<string, unknown>): Promise<unknown> => {
      return new Promise((resolve, reject) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          reject(new Error("Not connected"))
          return
        }
        const id = crypto.randomUUID()
        pendingRef.current.set(id, { resolve, reject })
        wsRef.current.send(
          JSON.stringify({ type: "command", id, tool, args }),
        )
        setTimeout(() => {
          const pending = pendingRef.current.get(id)
          if (pending) {
            pendingRef.current.delete(id)
            pending.reject(new Error("Command timed out"))
          }
        }, 10000)
      })
    },
    [],
  )

  return { status, sessionId, send }
}

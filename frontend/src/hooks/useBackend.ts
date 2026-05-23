import { useState, useEffect, useRef, useCallback } from "react"

type BackendStatus = "connecting" | "connected" | "disconnected" | "error"

interface UseBackendResult {
  status: BackendStatus
  sessionId: string | null
  send: (tool: string, args: Record<string, unknown>) => Promise<unknown>
}

export function useBackend(): UseBackendResult {
  const [status, setStatus] = useState<BackendStatus>("connecting")
  const [sessionId, setSessionId] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const pendingRef = useRef<Map<string, (value: unknown) => void>>(new Map())
  const connectRef = useRef<() => void>(null as unknown as () => void)

  const connect = useCallback(() => {
    const id = crypto.randomUUID()
    const ws = new WebSocket(`ws://127.0.0.1:9876/ws/${id}`)

    ws.onopen = () => {}

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === "connected") {
        setSessionId(msg.session_id)
        setStatus("connected")
      } else if (msg.type === "result") {
        const resolve = pendingRef.current.get(msg.id)
        if (resolve) {
          pendingRef.current.delete(msg.id)
          resolve(msg.ok ? msg.data : Promise.reject(new Error(msg.error)))
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
        pendingRef.current.set(id, resolve)
        wsRef.current.send(
          JSON.stringify({ type: "command", id, tool, args }),
        )
        setTimeout(() => {
          if (pendingRef.current.has(id)) {
            pendingRef.current.delete(id)
            reject(new Error("Command timed out"))
          }
        }, 10000)
      })
    },
    [],
  )

  return { status, sessionId, send }
}

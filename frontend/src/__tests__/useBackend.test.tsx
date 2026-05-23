import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useBackend } from "../hooks/useBackend"

class MockWebSocket {
  url: string
  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  readyState: number = WebSocket.CONNECTING
  sentMessages: string[] = []

  constructor(url: string) {
    this.url = url
  }

  send(data: string) {
    this.sentMessages.push(data)
  }

  close() {
    this.readyState = WebSocket.CLOSED
    this.onclose?.()
  }
}

describe("useBackend", () => {
  let mockWs: MockWebSocket

  beforeEach(() => {
    mockWs = new MockWebSocket("ws://localhost:9876/ws/test")
    vi.stubGlobal("WebSocket", function (this: MockWebSocket, url: string) {
      mockWs.url = url
      return mockWs
    } as unknown as typeof WebSocket)
    vi.stubGlobal("crypto", {
      randomUUID: vi.fn(() => "test-uuid"),
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("starts in connecting state", () => {
    const { result } = renderHook(() => useBackend())
    expect(result.current.status).toBe("connecting")
    expect(result.current.sessionId).toBeNull()
  })

  it("transitions to connected when server responds", () => {
    const { result } = renderHook(() => useBackend())
    act(() => {
      mockWs.onopen?.()
    })
    act(() => {
      mockWs.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({ type: "connected", session_id: "s1" }),
        }),
      )
    })
    expect(result.current.status).toBe("connected")
    expect(result.current.sessionId).toBe("s1")
  })

  it("transitions to disconnected and reconnects", () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useBackend())
    act(() => {
      mockWs.onopen?.()
      mockWs.close()
    })
    expect(result.current.status).toBe("disconnected")
    vi.useRealTimers()
  })

  it("sends command messages via send", () => {
    const { result } = renderHook(() => useBackend())
    act(() => {
      mockWs.onopen?.()
      mockWs.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({ type: "connected", session_id: "s1" }),
        }),
      )
    })
    mockWs.readyState = WebSocket.OPEN
    result.current.send("echo", { text: "hello" })
    expect(mockWs.sentMessages.length).toBe(1)
    const parsed = JSON.parse(mockWs.sentMessages[0])
    expect(parsed.type).toBe("command")
    expect(parsed.tool).toBe("echo")
    expect(parsed.args).toEqual({ text: "hello" })
  })
})

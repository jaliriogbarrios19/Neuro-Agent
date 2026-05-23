/// <reference types="vitest/config" />
import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import Sidebar from "../components/Sidebar"

const defaultProps = {
  status: "connected" as const,
  onRefresh: vi.fn(),
  onViewChange: vi.fn(),
  activeView: "notes" as const,
}

describe("Sidebar", () => {
  it("renders navigation buttons", () => {
    render(<Sidebar {...defaultProps} />)
    expect(screen.getByTitle("Notes")).toBeInTheDocument()
    expect(screen.getByTitle("Chat")).toBeInTheDocument()
    expect(screen.getByTitle("Slides")).toBeInTheDocument()
  })

  it("shows green dot when connected", () => {
    render(<Sidebar {...defaultProps} />)
    const dot = document.querySelector(".bg-green-400")
    expect(dot).toBeInTheDocument()
  })

  it("calls onRefresh when refresh clicked", () => {
    const onRefresh = vi.fn()
    render(<Sidebar {...defaultProps} onRefresh={onRefresh} />)
    screen.getByTitle("Refresh").click()
    expect(onRefresh).toHaveBeenCalled()
  })

  it("calls onViewChange when chat clicked", () => {
    const onViewChange = vi.fn()
    render(<Sidebar {...defaultProps} onViewChange={onViewChange} />)
    screen.getByTitle("Chat").click()
    expect(onViewChange).toHaveBeenCalledWith("chat")
  })
})

/// <reference types="vitest/config" />
import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import Sidebar from "../components/Sidebar"

describe("Sidebar", () => {
  it("renders navigation buttons", () => {
    render(<Sidebar status="connected" onRefresh={vi.fn()} />)
    expect(screen.getByTitle("Notes")).toBeInTheDocument()
    expect(screen.getByTitle("Research")).toBeInTheDocument()
    expect(screen.getByTitle("Chat")).toBeInTheDocument()
  })

  it("shows green dot when connected", () => {
    render(<Sidebar status="connected" onRefresh={vi.fn()} />)
    const dot = document.querySelector(".bg-green-400")
    expect(dot).toBeInTheDocument()
  })

  it("calls onRefresh when refresh clicked", () => {
    const onRefresh = vi.fn()
    render(<Sidebar status="connected" onRefresh={onRefresh} />)
    screen.getByTitle("Refresh").click()
    expect(onRefresh).toHaveBeenCalled()
  })
})

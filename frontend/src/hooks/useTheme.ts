import { useState } from "react"

export type Theme = "neural" | "paper" | "forest" | "ocean"

export const themeLabels: Record<Theme, string> = {
  neural: "Neural Dark",
  paper: "Paper Light",
  forest: "Forest",
  ocean: "Ocean",
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    return (localStorage.getItem("neuro-theme") as Theme) || "neural"
  })

  const setTheme = (t: Theme) => {
    localStorage.setItem("neuro-theme", t)
    document.documentElement.setAttribute("data-theme", t)
    setThemeState(t)
  }

  return { theme, setTheme }
}

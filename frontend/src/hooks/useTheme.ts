import { useState, useEffect } from "react"

export type Theme = "neural" | "paper" | "forest" | "ocean"

export const themeLabels: Record<Theme, string> = {
  neural: "Neural Dark",
  paper: "Paper Light",
  forest: "Forest",
  ocean: "Ocean",
}

function getSavedTheme(): Theme {
  return (localStorage.getItem("neuro-theme") as Theme) || "neural"
}

function applyTheme(t: Theme) {
  document.documentElement.setAttribute("data-theme", t)
  localStorage.setItem("neuro-theme", t)
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getSavedTheme)

  useEffect(() => {
    applyTheme(theme)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount
  }, [])

  const setTheme = (t: Theme) => {
    applyTheme(t)
    setThemeState(t)
  }

  return { theme, setTheme }
}

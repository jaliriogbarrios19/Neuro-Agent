import { Marp } from "@marp-team/marp-core"

const marp = new Marp()

self.onmessage = (e: MessageEvent<string>) => {
  try {
    const { html } = marp.render(e.data)
    self.postMessage(html)
  } catch {
    self.postMessage("<p style='color:red;padding:2rem'>Error rendering slides. Check your Markdown syntax.</p>")
  }
}

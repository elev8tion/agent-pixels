function ChatPageInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [input, setInput] = React.useState("")
  const [image, setImage] = React.useState<string | undefined>()
  const [isStreaming, setIsStreaming] = React.useState(false)
  const [lightboxHit, setLightboxHit] = React.useState<Hit | null>(null)
  const [lightboxHits, setLightboxHits] = React.useState<Hit[]>([])
  const messagesEndRef = React.useRef<HTMLDivElement>(null)
  const inputRef = React.useRef<HTMLTextAreaElement>(null)
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const abortRef = React.useRef<AbortController | null>(null)
  const handleSendRef = React.useRef<((text?: string, imageOverride?: string) => void) | null>(null)
  const didInitRef = React.useRef(false)

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  React.useEffect(() => {
    scrollToBottom()
  }, [messages])

  React.useEffect(() => {
    handleSendRef.current = handleSend
  })

  // Auto-send query handed off from the Search page (Ask mode)
  React.useEffect(() => {
    if (didInitRef.current) return
    const q = searchParams.get("q")
    // The attached image (if any) is passed via sessionStorage, since a
    // base64 image can't fit in a URL query param.
    let pendingImage: string | undefined
    if (searchParams.get("img")) {
      try {
        pendingImage = sessionStorage.getItem("pixelrag:pending-image") || undefined
        sessionStorage.removeItem("pixelrag:pending-image")
      } catch {
        pendingImage = undefined
      }
    }
    if (q || pendingImage) {
      didInitRef.current = true
      router.replace("/chat", { scroll: false })
      handleSendRef.current?.(q || "", pendingImage)
    }
-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleSend(text?: string, imageOverride?: string) {
    const query = (text ?? input).trim()
    const img = imageOverride ?? image
    if ((!query && !img) || isStreaming) return
    if (query) addHistory(query, "ask")
    const id1 = crypto.randomUUID?.() ?? "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => { const r = Math.random() * 16 | 0; return (c === "x" ? r : (r & 0x3 | 0x8)).toString(16) })
    const id2 = crypto.randomUUID?.() ?? "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => { const r = Math.random() * 16 | 0; return (c === "x" ? r : (r & 0x3 | 0x8)).toString(16) })
    const userMsg: ChatMessage = { id: id1, role: "user", content: query, image: img }
    const assistantMsg: ChatMessage = { id: id2, role: "assistant", content: "", searches: [] }
    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setInput("")
    setImage(undefined)
    setIsStreaming(true)
    const allMessages = [
      ...messages.filter((m) => m.content).map((m) => ({ role: m.role, content: m.content })),
      { role: "user" as const, content: query, ...(img ? { image: img } : {}) },
    ]
    const abort = new AbortController()
    abortRef.current = abort
    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: allMessages }),
        signal: abort.signal,
      })
      if (!resp.ok) { const err = await resp.json(); throw new Error(err.error || `HTTP ${resp.status}`) }
      const reader = resp.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""
        let eventType = ""
        for (const line of lines) {
          if (line.startsWith("event: ")) eventType = line.slice(7)
          else if (line.startsWith("data: ")) handleSSEEvent(assistantMsg.id, eventType, JSON.parse(line.slice(6)))
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setMessages((prev) => prev.map((m) => m.id === assistantMsg.id ? { ...m, content: m.content || `Error: ${err}`, searching: undefined } : m))
      }
    } finally { setIsStreaming(false); abortRef.current = null }
  }

  function handleSSEEvent(msgId: string, event: string, data: Record<string, unknown>) {
    setMessages((prev) => prev.map((m) => {
      if (m.id !== msgId) return m
      switch (event) {
        case "thinking": return { ...m, thinking: (m.thinking || "") + (data.text as string) }
        case "text": return { ...m, content: m.content + (data.text as string) }
        case "searching": return { ...m, searching: data.query as string }
        case "search_results": return { ...m, searching: undefined, searches: [...(m.searches || []), { query: data.query as string, hits: data.hits as SearchResult["hits"] }] }
        case "viewing_tile": return { ...m, viewingTile: true, tiles: [...(m.tiles || []), { article_id: data.article_id as number, tile_index: data.tile_index as number, chunk_index: data.chunk_index as number }] }
        case "done": return { ...m, searching: undefined, viewingTile: false }
        case "error": return { ...m, content: m.content || `Error: ${data.message}`, searching: undefined }
        default: return m
      }
    }))
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  function handleReset() {
    if (abortRef.current) abortRef.current.abort()
    setMessages([]); setIsStreaming(false); setInput(""); setImage(undefined); inputRef.current?.focus()
  }

  function handleTileClick(hit: Hit, allHits: Hit[]) {
    setLightboxHit(hit)
    setLightboxHits(allHits)
  }

  function handleFile(file: File) {
    if (!file.type.startsWith("image/")) return
    const reader = new FileReader()
    reader.onload = (e) => setImage(e.target?.result as string)
    reader.readAsDataURL(file)
  }

  function handlePaste(e: React.ClipboardEvent) {
    const file = Array.from(e.clipboardData.items)
      .find((it) => it.type.startsWith("image/"))
      ?.getAsFile()
    if (file) { e.preventDefault(); handleFile(file) }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const isEmpty = messages.length === 0

  return (
    <div className="chat-page flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <EmptyState onExample={handleSend} onSearchMode={() => router.push("/")} />
        ) : (
          <div className="mx-auto max-w-[720px] px-5 py-8">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <motion.div key={msg.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
                  {msg.role === "user" ? <UserMessage content={msg.content} image={msg.image} /> : <AssistantMessage message={msg} isStreaming={isStreaming && msg.id === messages[messages.length - 1]?.id} onTileClick={handleTileClick} />}
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        )}

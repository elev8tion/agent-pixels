export async function POST(req: Request) {
  const rawBody = await req.text()

  // Serverless (e.g. Vercel) can't run the Agent SDK — it needs the native
  // claude CLI binary + logged-in subscription credentials. When a self-hosted
  // agent backend is configured (running on a machine where claude is logged
  // in), proxy the SSE stream to it. Otherwise run the SDK inline (local dev).
  if (AGENT_BACKEND_URL) {
    try {
      const upstream = await fetch(`${AGENT_BACKEND_URL.replace(/\/$/, "")}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: rawBody,
      })
      return new Response(upstream.body, {
        status: upstream.status,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      })
    } catch (err) {
      return new Response(
        JSON.stringify({ error: `Agent backend unreachable: ${err}` }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      )
    }
  }

  const { messages: clientMessages } = JSON.parse(rawBody)
  if (!Array.isArray(clientMessages) || clientMessages.length === 0) {
    return new Response(
      JSON.stringify({ error: "messages required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    )
  }

  const conversationHistory = clientMessages
    .filter((m: { content: string }) => m.content)
    .map((m: { role: string; content: string }) => `${m.role}: ${m.content}`)
    .join("\n\n")

  const lastMessage = clientMessages[clientMessages.length - 1]
  const textPrompt =
    clientMessages.length === 1
      ? lastMessage.content || ""
      : `Previous conversation:\n${conversationHistory}\n\nRespond to the last user message.`

  // If the last user message carries an image, send a streaming prompt with an
  // image content block so Claude can see it (and search the index by it).
  const uploadedImage: string | null =
    typeof lastMessage?.image === "string" ? lastMessage.image : null

  let prompt: string | AsyncGenerator<SDKUserMessage>
  if (uploadedImage) {
    const m = uploadedImage.match(/^data:(image\/[a-z.+-]+);base64,(.+)$/i)
    const mediaType = m ? m[1] : "image/png"
    const data = m ? m[2] : uploadedImage
    const content = [
      ...(textPrompt ? [{ type: "text", text: textPrompt }] : []),
      { type: "image", source: { type: "base64", media_type: mediaType, data } },
    ]
    prompt = (async function* () {
      yield {
        type: "user",
        message: { role: "user", content },
        parent_tool_use_id: null,
      } as unknown as SDKUserMessage
    })()
  } else {
    prompt = textPrompt
  }

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder()
      function send(event: string, data: unknown) {
        controller.enqueue(encoder.encode(sseEvent(event, data)))
      }

      const tools = createTools(send, uploadedImage)
      const mcpServer = createSdkMcpServer({
        name: "pixelrag",
        version: "1.0.0",
        tools,
      })

      try {
        let sentText = false
        for await (const message of query({
          prompt,
          options: {
            systemPrompt: SYSTEM_PROMPT,
            mcpServers: { pixelrag: mcpServer },
            allowedTools: [
              "mcp__pixelrag__pixelrag_search",
              "mcp__pixelrag__pixelrag_tile",
            ],
            maxTurns: 8,
            maxBudgetUsd: parseFloat(
              process.env.CHAT_MAX_BUDGET_USD || "0.50"
            ),
            model: "sonnet",
          },
        })) {
          if (
            message.type === "assistant" &&
            "message" in message &&
            message.message
          ) {
            const msg = message.message as {
              content: Array<{
                type: string
                text?: string
              }>
            }
            for (const block of msg.content) {
              if (block.type === "text" && block.text) {
                send("text", { text: block.text })
                sentText = true
              }
            }
          }

          if (
            message.type === "result" &&
            message.subtype === "success" &&
            !sentText
          ) {
            send("text", { text: message.result })
          }
        }

        send("done", {})
      } catch (err) {
        send("error", { message: String(err) })
      } finally {
        controller.close()
      }
    },
  })

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  })
}

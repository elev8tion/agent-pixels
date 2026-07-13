async function expectEchoToolCall(baseURL: string, apiKey: string, model: string) {
	const client = new OpenAIClient(parseLLMConfig({ baseURL, apiKey, model }))
	const result = await client.invoke(PROMPT, { echo: ECHO_TOOL }, new AbortController().signal, {
		toolChoiceName: 'echo',
	})
	expect(result.toolResult).toBe('PING')
}

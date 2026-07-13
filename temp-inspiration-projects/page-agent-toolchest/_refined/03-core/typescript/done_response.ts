function doneResponse(text: string, success = true): Response {
	return agentResponse({ action: { done: { text, success } } })
}

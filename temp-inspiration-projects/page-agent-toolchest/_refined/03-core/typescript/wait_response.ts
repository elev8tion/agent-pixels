function waitResponse(seconds = 10): Response {
	return agentResponse({ action: { wait: { seconds } } })
}

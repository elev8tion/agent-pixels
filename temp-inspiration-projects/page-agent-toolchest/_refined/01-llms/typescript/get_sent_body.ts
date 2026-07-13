function getSentBody(fetchMock: ReturnType<typeof vi.fn>): Record<string, unknown> {
	const init = fetchMock.mock.calls[0][1] as RequestInit
	return JSON.parse(init.body as string)
}

function makeLLM(maxRetries = 2): LLM {
	return new LLM({
		baseURL: 'http://test.local/v1',
		model: 'gpt-5',
		maxRetries,
	})
}

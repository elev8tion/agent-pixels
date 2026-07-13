export function getProvider(baseURL?: string): 'openrouter' | undefined {
	if (!baseURL) return undefined
	try {
		const url = new URL(baseURL)
		const hostname = url.hostname
		if (hostname === 'openrouter.ai') return 'openrouter'
		return undefined
	} catch (e) {
		return undefined
	}
}

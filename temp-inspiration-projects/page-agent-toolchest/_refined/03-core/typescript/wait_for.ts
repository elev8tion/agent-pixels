export async function waitFor(seconds: number, signal?: AbortSignal): Promise<void> {
	if (!signal) {
		await new Promise((resolve) => setTimeout(resolve, seconds * 1000))
		return
	}
	signal.throwIfAborted()
	await new Promise<void>((resolve, reject) => {
		const timer = setTimeout(() => {
			signal.removeEventListener('abort', onAbort)
			resolve()
		}, seconds * 1000)
		const onAbort = () => {
			clearTimeout(timer)
			// reason is a DOMException AbortError.
			reject(signal.reason as DOMException)
		}
		signal.addEventListener('abort', onAbort, { once: true })
	})
}

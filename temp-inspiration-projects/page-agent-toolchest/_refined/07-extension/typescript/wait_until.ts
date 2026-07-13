async function waitUntil(
	check: () => boolean | Promise<boolean>,
	timeoutMS = 60_000,
	throwIfTimeout = false
): Promise<boolean> {
	if (await check()) return true

	return new Promise((resolve, reject) => {
		const start = Date.now()
		const poll = async () => {
			try {
				if (await check()) return resolve(true)
				if (Date.now() - start > timeoutMS) {
					if (throwIfTimeout) {
						return reject(new Error(`waitUntil timed out after ${timeoutMS}ms`))
					} else {
						return resolve(false)
					}
				}
				setTimeout(poll, 100)
			} catch (err) {
				reject(err instanceof Error ? err : new Error(String(err)))
			}
		}
		setTimeout(poll, 100)
	})
}

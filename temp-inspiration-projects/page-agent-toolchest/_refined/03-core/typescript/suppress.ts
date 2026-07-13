export async function suppress<T>(fn: () => T | Promise<T>): Promise<Awaited<T> | undefined> {
	try {
		return await fn()
	} catch (error) {
		console.error(error)
		return undefined
	}
}

export function getElementTextMap(simplifiedHTML: string) {
	const lines = simplifiedHTML
		.split('\n')
		.map((line) => line.trim())
		.filter((line) => line.length > 0)
	const elementTextMap = new Map<number, string>()
	for (const line of lines) {
		const regex = /^\[(\d+)\]<[^>]+>([^<]*)/
		const match = regex.exec(line)
		if (match) {
			const index = parseInt(match[1], 10)
			elementTextMap.set(index, line)
		}
	}

	return elementTextMap
}

function matchAttributes(
	attrs: Record<string, string>,
	patterns: string[]
): Record<string, string> {
	const result: Record<string, string> = {}

	for (const pattern of patterns) {
		if (pattern.includes('*')) {
			const regex = globToRegex(pattern)
			for (const key of Object.keys(attrs)) {
				if (regex.test(key) && attrs[key].trim()) {
					result[key] = attrs[key].trim()
				}
			}
		} else {
			const value = attrs[pattern]
			if (value && value.trim()) {
				result[pattern] = value.trim()
			}
		}
	}

	return result
}

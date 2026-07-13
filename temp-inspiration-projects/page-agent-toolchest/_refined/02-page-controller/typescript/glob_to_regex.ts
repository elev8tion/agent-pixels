function globToRegex(pattern: string): RegExp {
	let regex = globRegexCache.get(pattern)
	if (!regex) {
		const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&')
		regex = new RegExp(`^${escaped.replace(/\*/g, '.*')}$`)
		globRegexCache.set(pattern, regex)
	}
	return regex
}

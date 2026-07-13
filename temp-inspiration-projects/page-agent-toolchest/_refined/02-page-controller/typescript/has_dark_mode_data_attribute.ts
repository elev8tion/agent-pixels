function hasDarkModeDataAttribute() {
	const htmlElement = document.documentElement
	const bodyElement = document.body || document.documentElement // can be null in some cases

	const dataAttrs = ['data-theme', 'data-color-mode', 'data-bs-theme', 'data-mui-color-scheme']
	for (const attr of dataAttrs) {
		const bodyValue = bodyElement?.getAttribute(attr)
		const htmlValue = htmlElement.getAttribute(attr)

		if (bodyValue?.toLowerCase() === 'dark' || htmlValue?.toLowerCase() === 'dark') {
			return true
		}
	}

	return false
}

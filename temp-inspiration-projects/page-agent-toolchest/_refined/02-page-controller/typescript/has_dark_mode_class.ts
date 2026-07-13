function hasDarkModeClass() {
	const DEFAULT_DARK_MODE_CLASSES = ['dark', 'dark-mode', 'theme-dark', 'night', 'night-mode']

	const htmlElement = document.documentElement
	const bodyElement = document.body || document.documentElement // can be null in some cases

	// Check class names on <html> and <body>
	for (const className of DEFAULT_DARK_MODE_CLASSES) {
		if (htmlElement.classList.contains(className) || bodyElement?.classList.contains(className)) {
			return true
		}
	}

	return false
}

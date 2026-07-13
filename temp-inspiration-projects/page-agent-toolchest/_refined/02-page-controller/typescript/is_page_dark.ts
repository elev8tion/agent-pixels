export function isPageDark() {
	try {
		if (hasDarkModeClass()) return true
		if (hasDarkModeDataAttribute()) return true
		if (isColorSchemeDark()) return true
		if (isBackgroundDark()) return true
		if (isMainContentBackgroundDark()) return true
		if (isTextColorLight()) return true

		return false
	} catch (error) {
		console.warn('Error determining if page is dark:', error)
		return false
	}
}

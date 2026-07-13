function isTextColorLight() {
	/** Luminance (0-255) above which body text is considered light */
	const LIGHT_TEXT_LUMINANCE = 200

	const bodyStyle = window.getComputedStyle(document.body || document.documentElement)
	const luminance = getLuminance(bodyStyle.color)

	// Light text has high luminance (e.g. white text on dark bg)
	return luminance !== null && luminance > LIGHT_TEXT_LUMINANCE
}

function getLuminance(colorString: string): number | null {
	if (!colorString || colorString === 'transparent' || colorString.startsWith('rgba(0, 0, 0, 0)')) {
		return null // Transparent has no meaningful luminance
	}

	const rgb = parseRgbColor(colorString)
	if (!rgb) {
		return null // Could not parse color
	}

	// Standard perceived luminance formula
	return 0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b
}

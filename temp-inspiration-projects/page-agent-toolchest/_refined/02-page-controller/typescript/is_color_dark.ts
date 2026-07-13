function isColorDark(colorString: string, threshold = 128) {
	const luminance = getLuminance(colorString)
	return luminance !== null && luminance < threshold
}

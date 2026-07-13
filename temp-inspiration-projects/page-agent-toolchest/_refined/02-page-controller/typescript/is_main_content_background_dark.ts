function isMainContentBackgroundDark() {
	const { innerWidth: vw, innerHeight: vh } = window
	const minArea = vw * vh * 0.5

	const selectors = ['#app', '#root', '#__next']
	for (const selector of selectors) {
		const el = document.querySelector(selector)
		if (!el) continue

		const rect = el.getBoundingClientRect()
		if (rect.width * rect.height < minArea) continue

		if (isColorDark(window.getComputedStyle(el).backgroundColor)) return true
	}
	return false
}

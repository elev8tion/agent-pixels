function isColorSchemeDark() {
	// Check <meta name="color-scheme" content="dark">
	const meta = document.querySelector<HTMLMetaElement>('meta[name="color-scheme"]')
	const metaContent = meta?.content.toLowerCase()
	if (metaContent === 'dark' || metaContent === 'only dark') return true

	// Check the computed color-scheme CSS property on :root
	const rootStyle = window.getComputedStyle(document.documentElement)
	const colorScheme = rootStyle.getPropertyValue('color-scheme').trim().toLowerCase()
	return colorScheme === 'dark' || colorScheme === 'only dark'
}

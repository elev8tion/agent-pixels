export function getFlatTree(config: DomConfig): FlatDomTree {
	const viewportExpansion = resolveViewportExpansion(config.viewportExpansion)

	const interactiveBlacklist = [] as Element[]
	for (const item of config.interactiveBlacklist || []) {
		if (typeof item === 'function') {
			interactiveBlacklist.push(item())
		} else {
			interactiveBlacklist.push(item)
		}
	}

	const interactiveWhitelist = [] as Element[]
	for (const item of config.interactiveWhitelist || []) {
		if (typeof item === 'function') {
			interactiveWhitelist.push(item())
		} else {
			interactiveWhitelist.push(item)
		}
	}

	const elements = domTree({
		doHighlightElements: true,
		debugMode: true,
		focusHighlightIndex: -1,
		viewportExpansion,
		interactiveBlacklist,
		interactiveWhitelist,
		highlightOpacity: config.highlightOpacity ?? 0.0,
		highlightLabelOpacity: config.highlightLabelOpacity ?? 0.1,
	}) as FlatDomTree

	const currentUrl = window.location.href

	/**
	 * 标记新出现的元素
	 * @todo browser-use 使用 hash(位置，属性等信息) 来判断是否同一个元素，
	 *       能够解决 1. 元素被删除后重新添加 2. 页面卸载 等问题。
	 *       这里先简单做.
	 */
	for (const nodeId in elements.map) {
		const node = elements.map[nodeId]
		if (node.isInteractive && node.ref) {
			const ref = node.ref as HTMLElement
			// @note 这样太严格，元素是可以跨页面存在的
			// if (newElementsCache.get(ref) !== currentUrl) {
			if (!newElementsCache.has(ref)) {
				newElementsCache.set(ref, currentUrl)
				node.isNew = true
			}
		}
	}

	return elements
}

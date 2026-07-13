export function isHTMLElement(el: unknown): el is HTMLElement {
	// @todo either specify to HTMLElement or allow Element here.
	return !!el && (el as Node).nodeType === 1
}

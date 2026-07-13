export async function movePointerToElement(element: HTMLElement, x: number, y: number) {
	const offset = getIframeOffset(element)

	window.dispatchEvent(
		new CustomEvent('PageAgent::MovePointerTo', {
			detail: { x: x + offset.x, y: y + offset.y },
		})
	)

	await waitFor(0.3)
}

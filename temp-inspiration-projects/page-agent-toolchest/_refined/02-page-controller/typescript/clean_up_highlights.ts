export function cleanUpHighlights() {
	const cleanupFunctions = (window as any)._highlightCleanupFunctions || []
	for (const cleanup of cleanupFunctions) {
		if (typeof cleanup === 'function') {
			cleanup()
		}
	}

	;(window as any)._highlightCleanupFunctions = []
}

const DEFAULT_VIEWPORT_EXPANSION = -1

export function resolveViewportExpansion(viewportExpansion?: number): number {
	return viewportExpansion ?? DEFAULT_VIEWPORT_EXPANSION
}

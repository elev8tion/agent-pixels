function toOpenRouterModelId(brand: string, model: string): string {
	if (model in OPENROUTER_ID_OVERRIDES) return OPENROUTER_ID_OVERRIDES[model]
	const slug = OPENROUTER_VENDOR_SLUG[brand]
	if (!slug) throw new Error(`No OpenRouter vendor slug mapped for brand "${brand}"`)
	return `${slug}/${model.toLowerCase()}`
}

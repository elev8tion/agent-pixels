function isExecutingTool(detail: unknown, toolName: string): boolean {
	return (
		typeof detail === 'object' &&
		detail !== null &&
		'type' in detail &&
		'tool' in detail &&
		detail.type === 'executing' &&
		detail.tool === toolName
	)
}

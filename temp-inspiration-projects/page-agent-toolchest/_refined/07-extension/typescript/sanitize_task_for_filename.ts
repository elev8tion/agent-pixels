function sanitizeTaskForFilename(task: string): string {
	return task
		.trim()
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '')
		.slice(0, MAX_TASK_SLUG_LENGTH)
}

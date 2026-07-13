export function buildHistoryExportFilename(task: string, createdAt: number): string {
	const taskSlug = sanitizeTaskForFilename(task)
	const timestamp = formatTimestampForFilename(createdAt)

	return taskSlug
		? `${EXPORT_FILE_PREFIX}-${taskSlug}-${timestamp}.json`
		: `${EXPORT_FILE_PREFIX}-${timestamp}.json`
}

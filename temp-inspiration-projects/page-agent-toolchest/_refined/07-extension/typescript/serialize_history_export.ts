export function serializeHistoryExport(history: HistoricalEvent[]): string {
	return `${JSON.stringify(history, null, 2)}\n`
}

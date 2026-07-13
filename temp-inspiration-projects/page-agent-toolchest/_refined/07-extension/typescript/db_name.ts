const DB_NAME = 'page-agent-ext'
const DB_VERSION = 1

export interface SessionRecord {
	id: string
	task: string
	history: HistoricalEvent[]
	status: 'completed' | 'error' | 'stopped'
	createdAt: number
}

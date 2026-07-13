export async function clearSessions(): Promise<void> {
	const db = await getDB()
	await db.clear('sessions')
}

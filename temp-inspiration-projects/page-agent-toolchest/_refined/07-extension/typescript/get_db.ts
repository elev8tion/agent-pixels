function getDB() {
	if (!dbPromise) {
		dbPromise = openDB<PageAgentDB>(DB_NAME, DB_VERSION, {
			upgrade(db) {
				const store = db.createObjectStore('sessions', { keyPath: 'id' })
				store.createIndex('by-created', 'createdAt')
			},
		})
	}
	return dbPromise
}

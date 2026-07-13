function formatTimestampForFilename(createdAt: number): string {
	const date = new Date(createdAt)
	const year = date.getFullYear()
	const month = pad(date.getMonth() + 1)
	const day = pad(date.getDate())
	const hours = pad(date.getHours())
	const minutes = pad(date.getMinutes())
	const seconds = pad(date.getSeconds())

	return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`
}

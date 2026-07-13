export function uid() {
	const id = randomID(ids)
	ids.push(id)
	return id
}

function abortError(): Error {
	const err = new Error('aborted')
	err.name = 'AbortError'
	return err
}

async function getOwnWindowId(): Promise<number | undefined> {
	if (typeof chrome.windows === 'undefined') return undefined
	const win = await chrome.windows.getCurrent()
	return win.id
}

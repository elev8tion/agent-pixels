function sendMessage(message: {
	type: 'TAB_CONTROL'
	action: TabAction
	payload?: any
}): Promise<any> {

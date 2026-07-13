function onceActivity(
	agent: PageAgentCore,
	predicate: (detail: unknown) => boolean
): Promise<void> {
	return new Promise((resolve) => {
		const onActivity = (event: Event) => {
			if (!predicate((event as CustomEvent).detail)) return
			agent.removeEventListener('activity', onActivity)
			resolve()
		}

		agent.addEventListener('activity', onActivity)
	})
}

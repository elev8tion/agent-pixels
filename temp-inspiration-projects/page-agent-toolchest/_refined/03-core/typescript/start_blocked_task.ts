async function startBlockedTask(
	agent: PageAgentCore,
	task = 'first'
): Promise<{ result: Promise<ExecutionResult> }> {

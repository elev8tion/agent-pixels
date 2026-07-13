function agentResponse(args: unknown): Response {
	return new Response(
		JSON.stringify({
			choices: [
				{
					finish_reason: 'tool_calls',
					message: {
						tool_calls: [
							{
								function: {
									name: 'AgentOutput',
									arguments: JSON.stringify(args),
								},
							},
						],
					},
				},
			],
			usage: {},
		})
	)
}

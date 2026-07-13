function toolCallBody(toolName: string, args: unknown, finishReason = 'tool_calls') {
	return {
		choices: [
			{
				finish_reason: finishReason,
				message: {
					tool_calls: [
						{
							id: 'call_1',
							type: 'function',
							function: {
								name: toolName,
								arguments: typeof args === 'string' ? args : JSON.stringify(args),
							},
						},
					],
				},
			},
		],
		usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 },
	}
}

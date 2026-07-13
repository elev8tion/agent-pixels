export function modelPatch(body: Record<string, any>, baseURL?: string) {
	const model: string = body.model || ''
	if (!model) return body

	const provider = getProvider(baseURL)

	const modelName = normalizeModelName(model)

	if (modelName.startsWith('qwen')) {
		debug('Patch Qwen: disable thinking')
		body.enable_thinking = false
		if (body.temperature === undefined && !/max|plus/.test(modelName)) {
			debug('Patch Qwen: raise temperature to 1.0')
			body.temperature = 1.0
		}
	}

	if (modelName.startsWith('deepseek')) {
		debug('Patch DeepSeek: disable thinking, remove tool_choice')
		body.thinking = { type: 'disabled' }
		delete body.tool_choice
	}

	if (modelName.startsWith('gpt')) {
		if (modelName.startsWith('gpt-5')) {
			body.verbosity = 'low'

			// gpt-5 gpt-5-mini gpt-5-nano only supports "minimal";
			// 5.1+ supports "none".
			body.reasoning_effort = /^gpt-5(-|$)/.test(modelName) ? 'minimal' : 'none'
			debug(`Patch GPT-5: verbosity=low, reasoning_effort=${body.reasoning_effort}`)
		}

		if (modelName.includes('chat-latest')) {
			debug('Omitting reasoning_effort and temperature for chat-latest')
			delete body.reasoning_effort
			delete body.temperature
		}
	}

	if (modelName.startsWith('claude')) {
		if (/opus|sonnet|haiku/.test(modelName)) {
			debug('Patch Claude: disable thinking')
			body.thinking = { type: 'disabled' }

			if (provider !== 'openrouter') {
				// Convert tool_choice to Claude format
				if (body.tool_choice === 'required') {
					// 'required' -> { type: 'any' } (must call some tool)
					debug('Applying Claude patch: convert tool_choice "required" to { type: "any" }')
					body.tool_choice = { type: 'any' }
				} else if (body.tool_choice?.function?.name) {
					// { type: 'function', function: { name: '...' } } -> { type: 'tool', name: '...' }
					debug('Applying Claude patch: convert tool_choice format')
					body.tool_choice = { type: 'tool', name: body.tool_choice.function.name }
				}
			}
		} else {
			debug('Patch Claude: reasoning_effort=low')
			body.reasoning_effort = 'low'

			// Fable and mythos can not disable adaptive thinking.
			// Claude does not support tool_choice with extended thinking.
			// These 2 concepts are blurred. Basically no tool_choice with thinking.
			delete body.tool_choice
		}
	}

	if (modelName.startsWith('gemini')) {
		debug('Patch Gemini: reasoning_effort=low')
		body.reasoning_effort = 'low'
		if (/^gemini-25(?!.*pro)/.test(modelName)) {
			debug('Patch Gemini 2.5 non-Pro: reasoning_effort=none')
			body.reasoning_effort = 'none'
		} else if (
			modelName.startsWith('gemini-35-flash') ||
			modelName.startsWith('gemini-31-flash-lite') ||
			modelName.startsWith('gemini-3-flash')
		) {
			debug('Patch Gemini 3.x Flash/Lite: reasoning_effort=minimal')
			body.reasoning_effort = 'minimal'
		}
	}

	if (modelName.startsWith('glm')) {
		debug('Patch GLM: disable thinking')
		body.thinking = { type: 'disabled' }
	}

	if (modelName.startsWith('grok')) {
		if (/^grok-4-?3/.test(modelName)) {
			debug('Patch Grok 4.3: reasoning_effort=none')
			body.reasoning_effort = 'none'
		} else if (modelName.startsWith('grok-3-mini') || modelName.startsWith('grok-code-fast')) {
			debug('Patch Grok mini/code: reasoning_effort=low')
			body.reasoning_effort = 'low'
		}
	}

	if (modelName.startsWith('kimi')) {
		if (!modelName.includes('code')) {
			// kimi-k2.7-code cannot disable thinking
			debug('Patch Kimi: disable thinking')
			body.thinking = { type: 'disabled' }
		}
	}

	if (modelName.startsWith('minimax')) {
		debug('Patch MiniMax: remove parallel_tool_calls')
		delete body.parallel_tool_calls

		if (modelName.includes('m3')) {
			// Only M3 can disable thinking
			debug('Patch MiniMax: disable thinking')
			body.thinking = { type: 'disabled' }
		}
	}

	// provider patches

	if (provider === 'openrouter') {
		// openrouter use reasoning object instead of reasoning_effort

		const reasoningEffort = body.reasoning_effort
		const reasoningDisabled =
			body.thinking?.type === 'disabled' ||
			body.enable_thinking === false ||
			reasoningEffort === 'none'

		if (reasoningDisabled) {
			body.reasoning = { enabled: false }
		} else if (reasoningEffort) {
			body.reasoning = { enabled: true, effort: reasoningEffort }
		}
	}

	return body
}

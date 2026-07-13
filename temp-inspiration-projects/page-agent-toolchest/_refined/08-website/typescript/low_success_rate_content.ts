function LowSuccessRateContent(isZh: boolean) {
	return (
		<>
			<p className="text-sm text-gray-500 dark:text-gray-400 mb-4 italic">
				{isZh
					? '按以下顺序逐步排查，从最简单的情况开始：'
					: 'Follow this diagnostic funnel from simplest to most advanced:'}
			</p>
			<ol className="list-decimal pl-5 space-y-4 text-gray-700 dark:text-gray-300">
				<li>
					<strong>{isZh ? '先从简单指令开始' : 'Start with a simple instruction'}</strong>
					<p className="mt-1">
						{isZh
							? '给一个具体的、单步的简单指令（如"点击登录按钮"），看 Agent 能否完成。如果连简单操作都失败了，问题可能不在模型能力上。'
							: 'Give a concrete, single-step instruction (e.g. "click the login button"). If even simple actions fail, the issue is likely not model capability.'}
					</p>
				</li>
				<li>
					<strong>{isZh ? '尝试最强模型' : 'Try the strongest model available'}</strong>
					<p className="mt-1">
						{isZh
							? '切换到你能获取到的最先进、最大的模型，以排除是否是模型智能水平不足导致的问题。'
							: "Switch to the most capable model you have access to, to isolate whether it's a model intelligence issue."}
					</p>
				</li>
				<li>
					<strong>{isZh ? '优化指令质量' : 'Improve instruction quality'}</strong>
					<p className="mt-1">
						{isZh
							? '给出尽可能具体的指令。对于复杂任务，建议使用另一个 LLM 来预先拆分和细化用户的需求，然后逐步执行。'
							: "Be as specific as possible. For complex tasks, consider using another LLM to decompose and refine the user's request before execution."}
					</p>
				</li>
				<li>
					<strong>{isZh ? '提供充足的上下文' : 'Provide sufficient context'}</strong>
					<p className="mt-1">
						{isZh
							? '通过 instructions 配置注入网站背景描述、关键术语解释等上下文信息，帮助 Agent 更好地理解页面。'
							: 'Use the instructions config to inject website descriptions, key terminology, and background context to help the agent understand the page.'}
					</p>
				</li>
				<li>
					<strong>{isZh ? '检查 HTML 清洗结果' : 'Check HTML sanitization output'}</strong>
					<p className="mt-1">
						{isZh
							? '使用开发者工具检查清洗后的 HTML，确认关键信息、文本和可操作元素是否被正确保留。'
							: 'Inspect the sanitized HTML in dev tools to confirm that key information, text, and interactive elements are preserved correctly.'}
					</p>
				</li>
			</ol>
		</>
	)
}

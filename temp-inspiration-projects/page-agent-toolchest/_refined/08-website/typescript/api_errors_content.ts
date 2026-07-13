function ApiErrorsContent(isZh: boolean) {
	return (
		<div className="space-y-4 text-gray-700 dark:text-gray-300">
			<p>
				{isZh
					? '一些 LLM 供应商使用了与 OpenAI 不完全兼容的参数格式，导致请求参数校验失败。'
					: 'Some LLM providers use parameter formats that are not fully compatible with the OpenAI spec, causing request validation failures.'}
			</p>
			<div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
				<p className="font-medium mb-2">
					{isZh ? '解决方案：使用 customFetch' : 'Solution: use customFetch'}
				</p>
				<p className="text-sm mb-3">
					{isZh
						? '通过 customFetch 配置拦截请求，在发送前调整参数格式以适配目标供应商的要求。'
						: 'Use the customFetch config to intercept requests and adapt parameters before sending them to the target provider.'}
				</p>
				<CodeEditor
					code={`const agent = new PageAgent({
  // ...
  customFetch: async (url, init) => {
    // Adapt parameters for your provider
    const body = JSON.parse(init.body)
    delete body.tool_choice
    const bodyStr = JSON.stringify(body)

    return fetch(url, { ...init, body: bodyStr })
  },
})`}
				/>
			</div>
			<p className="text-sm">
				{isZh ? '参见 ' : 'See '}
				<Link
					href="/advanced/page-agent-core"
					className="text-blue-600 dark:text-blue-400 underline underline-offset-2"
				>
					PageAgentCore API
				</Link>
				{isZh ? ' 了解 customFetch 的完整用法。' : ' for full customFetch documentation.'}
			</p>
		</div>
	)
}

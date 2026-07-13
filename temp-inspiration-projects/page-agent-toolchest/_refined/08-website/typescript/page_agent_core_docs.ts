export default function PageAgentCoreDocs() {
	const { isZh } = useLanguage()

	return (
		<div>
			<h1 className="text-4xl font-bold mb-6">PageAgentCore</h1>

			<p className="text-xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
				{isZh
					? 'PageAgentCore 是不带 UI 的核心 Agent 类。用于需要自定义 UI 或无头运行的场景。'
					: 'PageAgentCore is the core Agent class without UI. Use it for custom UI or headless scenarios.'}
			</p>

			{/* When to use */}
			<section className="mb-10">
				<Heading id="when-to-use-pageagentcore">
					{isZh ? '何时使用 PageAgentCore' : 'When to Use PageAgentCore'}
				</Heading>
				<ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-2">
					<li>{isZh ? '需要自定义 UI 界面' : 'Need a custom UI interface'}</li>
					<li>{isZh ? '在自动化测试中无头运行' : 'Running headless in automated tests'}</li>
					<li>
						{isZh
							? '在非浏览器环境运行（需自定义 PageController）'
							: 'Running in non-browser environments (requires custom PageController)'}
					</li>
					<li>
						{isZh
							? '将 PageAgent 嵌入其他 Agent 系统'
							: 'Embedding PageAgent in other agent systems'}
					</li>
				</ul>
			</section>

			{/* Basic Usage */}
			<section className="mb-10">
				<Heading id="basic-usage">{isZh ? '基本用法' : 'Basic Usage'}</Heading>
				<CodeEditor
					language="typescript"
					code={`import { PageAgentCore } from '@page-agent/core'
import { PageController } from '@page-agent/page-controller'

const agent = new PageAgentCore({
  pageController: new PageController({ enableMask: true }),
  baseURL: 'https://api.openai.com/v1',
  apiKey: 'your-api-key',
  model: 'gpt-5.2',
})

// Listen to events for UI display
agent.addEventListener('statuschange', () => {
  console.log('Status:', agent.status)
})

agent.addEventListener('activity', (e) => {
  const activity = (e as CustomEvent).detail
  console.log('Activity:', activity.type)
})

// Execute task
const result = await agent.execute('Fill in the form with test data')`}
				/>
			</section>

			<APIDivider title={isZh ? '配置' : 'Configuration'} />

			{/* Configuration */}

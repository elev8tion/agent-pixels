export default function PageControllerDocs() {
	const { isZh } = useLanguage()

	return (
		<div>
			<h1 className="text-4xl font-bold mb-6">PageController</h1>

			<p className="text-xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
				{isZh
					? 'PageController 负责 DOM 提取和元素交互，独立于 LLM。它将页面状态结构化为 LLM 可消费的格式，并执行元素级操作。'
					: 'PageController handles DOM extraction and element interaction, independent of LLM. It structures page state into LLM-consumable format and executes element-level actions.'}
			</p>

			{/* Basic Usage */}
			<section className="mb-10">
				<Heading id="basic-usage">{isZh ? '基本用法' : 'Basic Usage'}</Heading>
				<p className="text-gray-600 dark:text-gray-400 mb-4">
					{isZh
						? 'PageAgent 接受 PageController 配置项：'
						: 'PageAgent accepts PageController options:'}
				</p>
				<CodeEditor
					language="typescript"
					code={`import { PageAgent } from 'page-agent'

const agent = new PageAgent({
  baseURL: 'https://api.openai.com/v1',
  apiKey: 'your-api-key',
  model: 'gpt-5.2',

  // PageController options
  enableMask: true,
  viewportExpansion: 0,
})`}
				/>
				<p className="text-gray-600 dark:text-gray-400 mt-4">
					{isZh
						? 'PageAgentCore 接受 PageController 实例：'
						: 'PageAgentCore accepts a PageController instance:'}
				</p>
				<CodeEditor
					language="typescript"
					code={`import { PageAgentCore } from '@page-agent/core'
import { PageController } from '@page-agent/page-controller'

const pageController = new PageController({
  enableMask: true,
  viewportExpansion: -1,  // extract full page
})

const agent = new PageAgentCore({
  pageController,
  baseURL: 'https://api.openai.com/v1',
  apiKey: 'your-api-key',
  model: 'gpt-5.2',
})`}
				/>
			</section>

			<APIDivider title={isZh ? '配置' : 'Configuration'} />

			{/* Configuration */}

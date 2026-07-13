export default function CustomUIDocs() {
	const { isZh } = useLanguage()

	return (
		<div>
			<h1 className="text-4xl font-bold mb-6">{isZh ? '自定义 UI' : 'Custom UI'}</h1>

			<p className="text-xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
				{isZh
					? 'PageAgent 的核心逻辑（PageAgentCore）和 UI 完全解耦，通过事件通讯。你可以用自己的 UI 替换内置 Panel。'
					: 'PageAgent core logic (PageAgentCore) is fully decoupled from UI through events. You can replace the built-in Panel with your own UI.'}
			</p>

			{/* Architecture */}
			<section className="mb-10">
				<Heading id="architecture">{isZh ? '架构' : 'Architecture'}</Heading>
				<p className="text-gray-600 dark:text-gray-400 mb-4">
					{isZh
						? 'PageAgent 由三个独立模块组成，可自由组合：'
						: 'PageAgent consists of three independent modules that can be freely combined:'}
				</p>
				<ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-2 mb-4">
					<li>
						<strong>PageAgentCore</strong> -{' '}
						{isZh ? '核心 Agent 逻辑，不包含 UI' : 'Core agent logic, no UI'}
					</li>
					<li>
						<strong>PageController</strong> -{' '}
						{isZh ? 'DOM 操作和视觉反馈' : 'DOM operations and visual feedback'}
					</li>
					<li>
						<strong>UI (Panel)</strong> -{' '}
						{isZh
							? '用户界面，可替换为自定义实现'
							: 'User interface, replaceable with custom implementation'}
					</li>
				</ul>
			</section>

			<APIDivider title={isZh ? '事件系统' : 'Event System'} />

			{/* Two Event Streams */}

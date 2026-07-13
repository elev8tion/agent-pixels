function WrongElementContent(isZh: boolean) {
	return (
		<ol className="list-decimal pl-5 space-y-4 text-gray-700 dark:text-gray-300">
			<li>
				<strong>{isZh ? '了解现实局限' : 'Understand the reality'}</strong>
				<p className="mt-1">
					{isZh
						? '并非所有网站都提供了完善的语义化 HTML 和 accessibility 标签。对于此类网站，DOM 清洗可能无法产出足够好的结果。'
						: 'Not all websites provide proper semantic HTML and accessibility labels. For such sites, DOM sanitization may not produce good enough results.'}
				</p>
			</li>
			<li>
				<strong>{isZh ? '检查目标元素类型' : 'Check target element type'}</strong>
				<p className="mt-1">
					{isZh
						? '确认目标元素是否为图片、Canvas、或需要复杂交互（如拖拽、基于坐标的点击）的元素。这些本身就超出了当前的能力范围。'
						: 'Verify if the target is an image, Canvas, or requires complex interactions (drag-and-drop, coordinate-based clicking). These are beyond current capabilities.'}
				</p>
			</li>
			<li>
				<strong>{isZh ? '检查清洗后的 HTML' : 'Inspect sanitized HTML'}</strong>
				<p className="mt-1">
					{isZh
						? '检查清洗结果中是否存在关键信息丢失、可操作元素未被编号等问题。'
						: 'Look for missing key information or unnumbered interactive elements in the sanitized output.'}
				</p>
			</li>
			<li>
				<strong>{isZh ? '注入 accessibility 增强' : 'Inject accessibility improvements'}</strong>
				<p className="mt-1">
					{isZh
						? '通过注入脚本为网站添加 aria-label、语义化标签等 accessibility 属性，改善 DOM 清洗质量。'
						: 'Inject scripts to add aria-labels, semantic attributes, and other a11y improvements to enhance DOM sanitization quality.'}
				</p>
			</li>
			<li>
				<strong>{isZh ? '开发专用 Tool' : 'Build a custom Tool'}</strong>
				<p className="mt-1">
					{isZh ? (
						<>
							对于特定的、持续难以操作的元素，考虑开发{' '}
							<Link
								href="/features/custom-tools"
								className="text-blue-600 dark:text-blue-400 underline underline-offset-2"
							>
								自定义 Tool
							</Link>{' '}
							来直接操作这些元素。
						</>
					) : (
						<>
							For consistently difficult elements, consider building a{' '}
							<Link
								href="/features/custom-tools"
								className="text-blue-600 dark:text-blue-400 underline underline-offset-2"
							>
								custom Tool
							</Link>{' '}
							to interact with them directly.
						</>
					)}
				</p>
			</li>
		</ol>
	)
}

export default function BetaNotice() {
	const { isZh } = useLanguage()

	return (
		<div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4 mb-8">
			<div className="flex items-start">
				<div className="shrink-0">
					<span className="text-xl">🚧</span>
				</div>
				<div className="ml-3">
					<h3 className="text-sm font-medium text-orange-800 dark:text-orange-200 mb-1">
						{isZh ? 'Beta 阶段' : 'Beta Stage'}
					</h3>
					<p className="text-sm text-orange-700 dark:text-orange-300">
						{isZh
							? '当前功能未完成，接口可能随时变更。正式版本发布前请勿用于生产环境。'
							: 'Current features are incomplete and the API may change at any time. Please do not use in production environments before the official release.'}
					</p>
				</div>
			</div>
		</div>
	)
}

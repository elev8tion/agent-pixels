export default function TroubleshootingPage() {
	const { isZh } = useLanguage()
	const sectionIds = SECTIONS.map((s) => s.id)
	const activeId = useActiveSection(sectionIds)

	return (
		<div className="max-w-5xl mx-auto">
			{/* Header */}
			<div className="mb-10">
				<h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">Troubleshooting</h1>
			</div>

			{/* Two-column: content + TOC */}
			<div className="flex gap-8">
				{/* Main content */}
				<div className="flex-1 min-w-0 space-y-12">
					{SECTIONS.map((section) => (
						<section key={section.id} className="scroll-mt-24">
							<Heading
								id={section.id}
								className="text-2xl font-bold mb-4 text-gray-900 dark:text-white"
							>
								{isZh ? section.title.zh : section.title.en}
							</Heading>

							{/* Symptom callout */}
							<div
								className={`border-l-4 px-4 py-3 rounded-r-lg mb-6 ${SYMPTOM_COLORS[section.color]}`}
							>
								<span className="text-xs font-semibold uppercase tracking-wider opacity-70">
									{isZh ? '症状' : 'Symptom'}
								</span>
								<p className="mt-1 text-sm">{isZh ? section.symptom.zh : section.symptom.en}</p>
							</div>

							{/* Diagnostic steps */}
							<div className="prose-sm">{section.content(isZh)}</div>
						</section>
					))}
				</div>

				{/* Right TOC */}
				<aside className="hidden lg:block w-48 shrink-0">
					<div className="sticky top-24">
						<h4 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3">
							{isZh ? '目录' : 'On this page'}
						</h4>
						<nav className="space-y-1">
							{SECTIONS.map((section) => (
								<button
									key={section.id}
									type="button"
									onClick={() =>
										document
											.getElementById(section.id)
											?.scrollIntoView({ behavior: 'smooth', block: 'start' })
									}
									className={`block cursor-pointer py-1 text-left text-sm transition-colors ${
										activeId === section.id
											? 'text-blue-600 dark:text-blue-400 font-medium'
											: 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
									}`}
								>
									{isZh ? section.title.zh : section.title.en}
								</button>
							))}
						</nav>
					</div>
				</aside>
			</div>
		</div>
	)
}

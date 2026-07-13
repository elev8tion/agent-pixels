export function patchReact(pageController: PageController) {
	const reactRootElements = document.querySelectorAll(
		'[data-reactroot], [data-reactid], [data-react-checksum], #root, #app, [id^="root-"], [id^="app-"], #adex-wrapper, #adex-root'
	)

	for (const element of reactRootElements) {
		element.setAttribute('data-page-agent-not-interactive', 'true')
	}
}

function createPageController(): PageController {
	const browserState: BrowserState = {
		url: 'https://example.test/',
		title: 'Test page',
		header: '',
		content: '',
		footer: '',
	}

	return {
		showMask: vi.fn(async () => {}),
		hideMask: vi.fn(),
		cleanUpHighlights: vi.fn(),
		getLastUpdateTime: vi.fn(() => Date.now()),
		getBrowserState: vi.fn(async () => browserState),
		dispose: vi.fn(),
	} as unknown as PageController
}

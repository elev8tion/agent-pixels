const navigation = (window as any).navigation
if (navigation && typeof navigation.addEventListener === 'function') {
	navigation.addEventListener('navigate', () => {
		// console.log('Navigation event detected, highlights cleaned up.')
		cleanUpHighlights()
	})
} else {

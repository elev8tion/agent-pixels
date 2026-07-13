export function patchAntd(pageController: PageController) {
	pageController.addEventListener('beforeUpdate', fixAntdSelect)
	pageController.addEventListener('afterUpdate', () => {
		for (const fn of clearFunctions) fn()
		clearFunctions.length = 0
	})
}

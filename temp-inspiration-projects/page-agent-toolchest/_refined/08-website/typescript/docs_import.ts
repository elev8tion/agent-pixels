const docsImport = () => import('./pages/docs')
const DocsPages = lazy(docsImport)

function ScrollToTop() {
	const [pathname] = useLocation()
	useLayoutEffect(() => {
		window.scrollTo(0, 0)
	}, [pathname])
	return null
}

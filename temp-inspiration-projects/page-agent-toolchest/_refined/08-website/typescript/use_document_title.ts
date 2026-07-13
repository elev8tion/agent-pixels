export function useDocumentTitle(title?: string) {
	useEffect(() => {
		document.title = title ? `${title} - PageAgent` : DEFAULT_TITLE
	}, [title])
}

function useActiveSection(ids: string[]) {
	const [activeId, setActiveId] = useState(ids[0])
	const observerRef = useRef<IntersectionObserver | null>(null)

	useEffect(() => {
		observerRef.current?.disconnect()

		const visibleEntries = new Map<string, number>()

		observerRef.current = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) {
						visibleEntries.set(entry.target.id, entry.intersectionRatio)
					} else {
						visibleEntries.delete(entry.target.id)
					}
				}
				// Pick the first visible section in document order
				const firstVisible = ids.find((id) => visibleEntries.has(id))
				if (firstVisible) setActiveId(firstVisible)
			},
			{ rootMargin: '-80px 0px -60% 0px', threshold: [0, 0.25] }
		)

		for (const id of ids) {
			const el = document.getElementById(id)
			if (el) observerRef.current.observe(el)
		}

		return () => observerRef.current?.disconnect()
	}, [ids])

	return activeId
}

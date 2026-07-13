export function useGitHubStars() {
	const [stars, setStars] = useState(cached)

	useEffect(() => {
		if (cached !== null) return
		const controller = new AbortController()
		fetch(STATS_URL, { signal: controller.signal })
			.then((r) => r.json())
			.then((data) => {
				cached = data.stargazers_count ?? null
				setStars(cached)
			})
			.catch(() => {})
		return () => controller.abort()
	}, [])

	return stars
}

function spaRoutes() {
	return {
		name: 'spa-routes',
		closeBundle() {
			const dist = resolve(__dirname, 'dist')
			const src = join(dist, 'index.html')
			for (const route of SPA_ROUTES) {
				const dir = join(dist, route)
				mkdirSync(dir, { recursive: true })
				copyFileSync(src, join(dir, 'index.html'))
			}
			console.log(`  ✓ Copied index.html to ${SPA_ROUTES.length} SPA routes`)

			const today = new Date().toISOString().split('T')[0]
			const urls = ['', ...SPA_ROUTES]
				.map(
					(route) =>
						`  <url>\n    <loc>${SITE_URL}/${route}</loc>\n    <lastmod>${today}</lastmod>\n  </url>`
				)
				.join('\n')
			writeFileSync(
				join(dist, 'sitemap.xml'),
				`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`
			)
			console.log(`  ✓ Generated sitemap.xml with ${SPA_ROUTES.length + 1} URLs`)
		},
	}
}

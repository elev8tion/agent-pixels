function getInjection(cdnSource: 'china' | 'international', isZh?: boolean) {
	const cdn = cdnSource === 'china' ? CDN_DEMO_CN_URL : CDN_DEMO_URL
	const locale = isZh ? 'zh-CN' : 'en-US'

	const injection = encodeURI(
		`javascript:(function(){var s=document.createElement('script');s.src=\`${cdn}?lang=${locale}&t=\${Math.random()}\`;s.setAttribute('crossorigin', true);s.type="text/javascript";s.onload=()=>console.log('PageAgent script loaded!');document.body.appendChild(s);})();`
	)

	return `
	<a
		href=${injection}
		class="inline-flex items-center text-xs px-3 py-2 bg-blue-500 text-white font-medium rounded-lg hover:shadow-md transform hover:scale-105 transition-all duration-200 cursor-move border-2 border-dashed border-green-300"
		draggable="true"
		onclick="return false;"
		title="Drag me to your bookmarks bar!"
	>
		✨PageAgent
	</a>
	`
}

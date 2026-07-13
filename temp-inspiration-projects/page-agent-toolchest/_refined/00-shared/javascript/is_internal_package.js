function isInternalPackage(name) {
	return name === 'page-agent' || name.startsWith('@page-agent/')
}

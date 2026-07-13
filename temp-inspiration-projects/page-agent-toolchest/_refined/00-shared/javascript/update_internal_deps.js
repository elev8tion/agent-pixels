function updateInternalDeps(deps, newVersion) {
	if (!deps) return false
	let changed = false
	for (const [name, version] of Object.entries(deps)) {
		if (isInternalPackage(name) && version !== newVersion) {
			deps[name] = newVersion
			changed = true
		}
	}
	return changed
}

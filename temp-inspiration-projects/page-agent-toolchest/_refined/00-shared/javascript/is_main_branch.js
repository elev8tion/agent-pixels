function isMainBranch() {
	if (process.env.GITHUB_REF) return process.env.GITHUB_REF === 'refs/heads/main'
	try {
		return execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf-8' }).trim() === 'main'
	} catch {
		return true
	}
}

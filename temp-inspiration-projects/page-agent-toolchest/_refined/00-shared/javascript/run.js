function run(label, command) {
	console.log(chalk.bgBlue.white.bold(` ▸ ${label} `))
	execSync(command, { stdio: 'inherit' })
}

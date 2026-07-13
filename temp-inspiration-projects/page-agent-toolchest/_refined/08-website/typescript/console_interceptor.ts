class ConsoleInterceptor {
	private static instance: ConsoleInterceptor
	private subscribers = new Set<(type: string, args: unknown[]) => void>()
	private originalConsole: {
		log: typeof console.log
		warn: typeof console.warn
		error: typeof console.error
	}
	private isIntercepting = false

	private constructor() {
		this.originalConsole = {
			log: console.log.bind(console),
			warn: console.warn.bind(console),
			error: console.error.bind(console),
		}
	}

	static getInstance() {
		if (!ConsoleInterceptor.instance) {
			ConsoleInterceptor.instance = new ConsoleInterceptor()
		}
		return ConsoleInterceptor.instance
	}

	subscribe(callback: (type: string, args: unknown[]) => void) {
		this.subscribers.add(callback)
		this.startIntercepting()
	}

	unsubscribe(callback: (type: string, args: unknown[]) => void) {
		this.subscribers.delete(callback)
		if (this.subscribers.size === 0) {
			this.stopIntercepting()
		}
	}

	private startIntercepting() {
		if (this.isIntercepting) return

		this.isIntercepting = true

		console.log = (...args: unknown[]) => {
			this.originalConsole.log(...args)
			this.notifySubscribers('log', args)
		}

		console.warn = (...args: unknown[]) => {
			this.originalConsole.warn(...args)
			this.notifySubscribers('warn', args)
		}

		console.error = (...args: unknown[]) => {
			this.originalConsole.error(...args)
			this.notifySubscribers('error', args)
		}
	}

	private stopIntercepting() {
		if (!this.isIntercepting) return

		this.isIntercepting = false
		console.log = this.originalConsole.log
		console.warn = this.originalConsole.warn
		console.error = this.originalConsole.error
	}

	private notifySubscribers(type: string, args: unknown[]) {
		this.subscribers.forEach((callback) => {
			callback(type, args)
		})
	}
}

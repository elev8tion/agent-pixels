const PROVIDERS = {
	openrouter: {
		baseURL: 'https://openrouter.ai/api/v1',
		apiKey: process.env.TESTING_OPENROUTER_KEY,
	},
	aliyun: {
		baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
		apiKey: process.env.TESTING_ALIYUN_KEY,
	},
	deepseek: {
		baseURL: 'https://api.deepseek.com',
		apiKey: process.env.TESTING_DEEPSEEK_KEY,
	},
} as const

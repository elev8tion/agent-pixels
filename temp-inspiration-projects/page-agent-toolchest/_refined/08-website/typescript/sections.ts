const SECTIONS: TroubleshootingSection[] = [
	{
		id: 'format-errors',
		title: { en: 'Model Response Format Errors', zh: '模型返回格式错误' },
		symptom: {
			en: 'The model returns malformed tool calls, plain text, or unexpected JSON instead of structured actions.',
			zh: '模型返回了格式错误的 tool call、纯文本或非预期的 JSON，而非结构化的操作指令。',
		},
		color: 'amber',
		content: FormatErrorsContent,
	},

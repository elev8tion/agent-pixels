function highlightSyntax(code: string): string {
	// 构建正则模式，包含更多 token 类型（在原始文本上匹配）
	const pattern = new RegExp(

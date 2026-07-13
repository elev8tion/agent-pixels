export function Highlighter({
	children,
	action = 'highlight',
	color = '#ffd1dc',
	strokeWidth = 1.5,
	animationDuration = 600,
	iterations = 2,
	padding = 2,
	multiline = true,
	isView = false,
}: HighlighterProps) {

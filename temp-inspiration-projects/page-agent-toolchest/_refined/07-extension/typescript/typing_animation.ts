export function TypingAnimation({
	children,
	words,
	className,
	duration = 100,
	typeSpeed,
	deleteSpeed,
	delay = 0,
	pauseDelay = 1000,
	loop = false,
	as: Component = 'span',
	startOnView = true,
	showCursor = true,
	blinkCursor = true,
	cursorStyle = 'line',
	...props
}: TypingAnimationProps) {

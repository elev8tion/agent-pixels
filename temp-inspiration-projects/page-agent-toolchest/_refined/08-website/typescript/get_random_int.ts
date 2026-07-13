const getRandomInt = (max: number): number => Math.floor(Math.random() * max)

export function HyperText({
	children,
	className,
	duration = 800,
	delay = 0,
	as: Component = 'div',
	startOnView = false,
	animateOnHover = true,
	characterSet = DEFAULT_CHARACTER_SET,
	...props
}: HyperTextProps) {

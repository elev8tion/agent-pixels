export function BlurFade({
	children,
	className,
	variant,
	duration = 0.4,
	delay = 0,
	offset = 6,
	direction = 'down',
	inView = false,
	inViewMargin = '-50px',
	blur = '6px',
	...props
}: BlurFadeProps) {

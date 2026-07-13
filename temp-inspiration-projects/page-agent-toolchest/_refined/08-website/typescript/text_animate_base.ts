const TextAnimateBase = ({
	children,
	delay = 0,
	duration = 0.3,
	variants,
	className,
	segmentClassName,
	as: Component = 'p',
	startOnView = true,
	once = false,
	by = 'word',
	animation = 'fadeIn',
	accessible = true,
	...props
}: TextAnimateProps) => {

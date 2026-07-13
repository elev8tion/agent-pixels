export const SparklesText: React.FC<SparklesTextProps> = ({
	children,
	colors = { first: '#9E7AFF', second: '#FE8BBB' },
	className,
	sparklesCount = 10,
	...props
}) => {

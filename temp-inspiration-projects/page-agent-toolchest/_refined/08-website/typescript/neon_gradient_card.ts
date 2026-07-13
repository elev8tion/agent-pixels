export const NeonGradientCard: React.FC<NeonGradientCardProps> = ({
	className,
	children,
	borderSize = 2,
	borderRadius = 20,
	neonColors = {
		firstColor: '#ff00aa',
		secondColor: '#00FFF1',
	},
	...props
}) => {

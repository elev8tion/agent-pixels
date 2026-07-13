export const Particles: React.FC<ParticlesProps> = ({
	className = '',
	quantity = 100,
	staticity = 50,
	ease = 50,
	size = 0.4,
	refresh = false,
	color = '#ffffff',
	vx = 0,
	vy = 0,
	...props
}) => {

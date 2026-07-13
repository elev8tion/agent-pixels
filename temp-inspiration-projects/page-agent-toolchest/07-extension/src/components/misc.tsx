import type { AgentStatus } from '@page-agent/core'
import { Motion } from 'ai-motion'
import { BookOpen, Globe } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { siGithub } from 'simple-icons'

import { TypingAnimation } from '@/components/ui/typing-animation'
import { cn } from '@/lib/utils'

// Status dot indicator
export function StatusDot({ status }: { status: AgentStatus }) {
	const colorClass = {
		idle: 'bg-muted-foreground',
		running: 'status-dot-cyan',
		completed: 'status-dot-success',
		error: 'status-dot-error',
		stopped: 'bg-muted-foreground',
	}[status]

	const label = {
		idle: 'Ready',
		running: 'Running',
		completed: 'Done',
		error: 'Error',
		stopped: 'Stopped',
	}[status]

	return (
		<div className="flex items-center gap-1.5 mr-2">
			<span
				className={cn('size-[7px] rounded-full', colorClass, status === 'running' && 'animate-pulse')}
			/>
			<span className="text-[10px] text-muted-foreground/80">{label}</span>
		</div>
	)
}

export function Logo({ className, variant = 'letters' }: { className?: string; variant?: 'full' | 'letters' | 'icon' }) {
	const src =
		variant === 'full'
			? '/assets/agentpixel.png'
			: variant === 'letters'
				? '/assets/agentpixel-letters.png'
				: '/assets/page-agent-64.png'

	return (
		<img
			src={src}
			alt="Agent Pixel"
			className={cn(
				'select-none',
				variant === 'full' && 'max-h-20 w-auto object-contain',
				variant === 'letters' && 'h-6 w-auto object-contain',
				variant === 'icon' && 'size-5',
				className
			)}
		/>
	)
}

// Premium glass navbar — always uses the project's 12px curved radius aesthetic
export function GlassNavbar({
	left,
	right,
	className,
}: {
	left?: React.ReactNode
	right?: React.ReactNode
	className?: string
}) {
	return (
		<div
			className={cn(
				'flex items-center justify-between border-b px-3 py-[7px]',
				'bg-background/95 backdrop-blur-xl',
				'border-[var(--glass-border)]',
				'rounded-t-[var(--radius)]', // 12px everywhere
				className
			)}
		>
			{left}
			{right}
		</div>
	)
}

// Full-screen ai-motion glow overlay, shown only while running
export function MotionOverlay({ active }: { active: boolean }) {
	const containerRef = useRef<HTMLDivElement>(null)
	const motionRef = useRef<Motion | null>(null)

	useEffect(() => {
		try {
			const mode = document.documentElement.classList.contains('dark') ? 'dark' : 'light'
			const motion = new Motion({
				mode,
				borderWidth: 4,
				borderRadius: 14,
				glowWidth: mode === 'dark' ? 120 : 60,
				styles: { position: 'absolute', inset: '0' },
			})
			motionRef.current = motion
			containerRef.current!.appendChild(motion.element)
			motion.autoResize(containerRef.current!)
		} catch (e) {
			console.warn('[MotionOverlay] Motion unavailable:', e)
		}

		return () => {
			motionRef.current?.dispose()
			motionRef.current = null
		}
	}, [])

	useEffect(() => {
		const motion = motionRef.current
		if (!motion) return

		let disposed = false
		if (active) {
			motion.start()
			motion.fadeIn()
		} else {
			motion.fadeOut().then(() => !disposed && motion.pause())
		}
		return () => {
			disposed = true
		}
	}, [active])

	return (
		<div
			ref={containerRef}
			className="pointer-events-none absolute inset-0 z-10 opacity-60 overflow-hidden"
			style={{ display: active ? undefined : 'none' }}
		/>
	)
}

// Empty state with beautiful full Agent Pixel logo (modern aesthetic treatment)
export function EmptyState() {
	return (
		<div className="flex flex-col items-center justify-center h-full gap-5 text-center px-6">
			<div className="relative select-none pointer-events-none">
				{/* Layered modern glows matching the logo's electric blue + purple */}
				<div className="absolute -inset-8 rounded-full bg-[radial-gradient(circle_at_50%_40%,rgba(57,182,255,0.18),transparent_70%)]" />
				<div className="absolute -inset-5 rounded-[22px] bg-[conic-gradient(from_200deg,var(--accent-cyan)_0deg,var(--accent-purple)_120deg,var(--accent-cyan)_240deg,var(--accent-purple)_360deg)] opacity-30 blur-3xl animate-[glow-a_7s_ease-in-out_infinite]" />
				<div className="absolute -inset-3 rounded-[18px] bg-[conic-gradient(from_30deg,var(--accent-purple),var(--accent-cyan),var(--accent-purple))] opacity-25 blur-2xl animate-[glow-b_6s_ease-in-out_infinite]" />

				{/* The stunning full logo */}
				<Logo variant="full" className="relative z-10 max-h-[148px] w-auto drop-shadow-[0_8px_32px_rgba(0,0,0,0.45)]" />
			</div>

			<div className="max-w-[260px]">
				<TypingAnimation
					className="text-[13px] text-muted-foreground"
					words={[
						'Automate pages with precision',
						'Run multi-page workflows',
						'Control from any website',
						'Professional browser agent',
					]}
					cursorStyle="underscore"
					loop
					startOnView={false}
					typeSpeed={18}
					deleteSpeed={9}
					pauseDelay={2800}
				/>
			</div>

			<div className="flex items-center gap-4 mt-1 text-muted-foreground">
				<a
					href="https://github.com/alibaba/page-agent"
					target="_blank"
					rel="noopener noreferrer"
					className="hover:text-foreground transition-colors"
					title="GitHub"
				>
					<svg role="img" viewBox="0 0 24 24" className="size-4 fill-current">
						<path d={siGithub.path} />
					</svg>
				</a>
				<a
					href="https://alibaba.github.io/page-agent/docs/features/chrome-extension"
					target="_blank"
					rel="noopener noreferrer"
					className="hover:text-foreground transition-colors"
					title="Docs"
				>
					<BookOpen className="size-4" />
				</a>
				<a
					href="https://alibaba.github.io/page-agent"
					target="_blank"
					rel="noopener noreferrer"
					className="hover:text-foreground transition-colors"
					title="Website"
				>
					<Globe className="size-4" />
				</a>
			</div>
		</div>
	)
}

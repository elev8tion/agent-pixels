import { useState } from 'react'
import type { ExtConfig } from '@/agent/useAgent'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type PiModel = {
	id: string
	name?: string
	reasoning?: boolean
	contextWindow?: number
	maxTokens?: number
	cost?: { input?: number; output?: number }
	thinkingLevelMap?: Record<string, string | null>
}

type PiProvider = {
	name: string
	baseUrl: string
	apiKey?: string
	models: PiModel[]
}

type ParsedModels = Record<string, PiProvider>

const REASONING_LEVELS = ['off', 'minimal', 'low', 'medium', 'high', 'xhigh'] as const
export type ReasoningEffort = (typeof REASONING_LEVELS)[number]

interface ModelPickerProps {
	onSelect: (config: Partial<ExtConfig> & { reasoningEffort?: ReasoningEffort }) => void
	currentBaseURL?: string
	currentModel?: string
	currentReasoningEffort?: ReasoningEffort
}

export function ModelPicker({ onSelect, currentBaseURL, currentModel, currentReasoningEffort }: ModelPickerProps) {
	const [parsed, setParsed] = useState<ParsedModels | null>(null)
	const [selectedProviderKey, setSelectedProviderKey] = useState<string>('')
	const [selectedModelId, setSelectedModelId] = useState<string>('')
	const [reasoningEffort, setReasoningEffort] = useState<ReasoningEffort>(currentReasoningEffort ?? 'medium')
	const [error, setError] = useState<string>('')
	const [syncing, setSyncing] = useState(false)

	const selectedProvider = selectedProviderKey ? parsed?.[selectedProviderKey] : null
	const selectedModel = selectedModelId ? selectedProvider?.models.find(m => m.id === selectedModelId) : null
	const supportsReasoning = !!selectedModel?.reasoning

	// Try to fetch from local Pi sync server
	const handleSyncFromPi = async () => {
		setSyncing(true)
		setError('')
		try {
			const res = await fetch('http://localhost:17321/pi-models', { cache: 'no-store' })
			if (!res.ok) throw new Error('Server not responding')
			const json = await res.json()
			if (json.providers) {
				setParsed(json.providers)
				setError('')
			} else {
				setError('Invalid response from local server')
			}
		} catch (e) {
			setError('Could not reach local sync server. Run the helper script first.')
		} finally {
			setSyncing(false)
		}
	}

	const handleFile = (file: File) => {
		const reader = new FileReader()
		reader.onload = (e) => {
			try {
				const json = JSON.parse(e.target?.result as string)
				if (json.providers) {
					setParsed(json.providers)
					setError('')
				} else {
					setError('Invalid models.json (no providers)')
				}
			} catch {
				setError('Failed to parse file')
			}
		}
		reader.readAsText(file)
	}

	const handlePaste = (text: string) => {
		try {
			const json = JSON.parse(text.trim())
			if (json.providers) {
				setParsed(json.providers)
				setError('')
			} else setError('Invalid format')
		} catch {
			setError('Invalid JSON')
		}
	}

	const applySelection = () => {
		if (!selectedProvider || !selectedModelId) return

		onSelect({
			baseURL: selectedProvider.baseUrl,
			model: selectedModelId,
			reasoningEffort: supportsReasoning ? reasoningEffort : undefined,
		})
	}

	const providers = parsed ? Object.keys(parsed) : []

	const formatCost = (cost?: PiModel['cost']) => {
		if (!cost || (cost.input === 0 && cost.output === 0)) return 'Free'
		return `$${cost.input}/${cost.output}`
	}

	return (
		<div className="space-y-3">
			<div className="flex items-center gap-2 flex-wrap">
				<Button
					variant="outline"
					size="sm"
					className="text-xs h-7"
					onClick={() => {
						const input = document.createElement('input')
						input.type = 'file'
						input.accept = '.json'
						input.onchange = (e) => {
							const f = (e.target as HTMLInputElement).files?.[0]
							if (f) handleFile(f)
						}
						input.click()
					}}
				>
					Import models.json
				</Button>

				<Button
					variant="outline"
					size="sm"
					className="text-xs h-7"
					onClick={handleSyncFromPi}
					disabled={syncing}
				>
					{syncing ? 'Syncing…' : 'Sync from local Pi'}
				</Button>

				<button
					onClick={() => {
						const txt = prompt('Paste ~/.pi/agent/models.json content')
						if (txt) handlePaste(txt)
					}}
					className="text-[10px] text-muted-foreground hover:text-foreground underline"
				>
					or paste JSON
				</button>
			</div>

			{!parsed && (
				<div className="text-[10px] text-muted-foreground/60 leading-snug">
					Run <code className="font-mono bg-muted px-1 rounded">npm run sync-pi</code> then click "Sync from local Pi", or import your models.json.
				</div>
			)}

			{error && (
				<div className="text-xs text-destructive bg-destructive/5 p-2 rounded">
					{error}
					{error.includes('local sync') && (
						<div className="mt-1 text-[10px]">
							Run in terminal: <code className="font-mono">node scripts/sync-pi-models.js</code>
						</div>
					)}
				</div>
			)}

			{parsed && (
				<div className="space-y-2 border rounded-xl p-3 bg-muted/20">
					<div className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wider mb-1">
						Your Pi Models • {providers.length} providers
					</div>

					<select
						value={selectedProviderKey}
						onChange={(e) => {
							const key = e.target.value
							setSelectedProviderKey(key)
							const first = parsed[key]?.models?.[0]?.id || ''
							setSelectedModelId(first)
						}}
						className="w-full h-8 text-xs rounded-lg border bg-background px-2"
					>
						<option value="">Choose provider…</option>
						{providers.map((key) => (
							<option key={key} value={key}>
								{parsed[key].name || key}
							</option>
						))}
					</select>

					{selectedProvider && (
						<select
							value={selectedModelId}
							onChange={(e) => setSelectedModelId(e.target.value)}
							className="w-full h-8 text-xs rounded-lg border bg-background px-2"
						>
							<option value="">Choose model…</option>
							{selectedProvider.models.map((m) => (
								<option key={m.id} value={m.id}>
									{m.name || m.id} {m.reasoning ? '• reasoning' : ''}
								</option>
							))}
						</select>
					)}

					{selectedModel && (
						<div className="text-[10px] text-muted-foreground flex gap-2 flex-wrap pt-0.5">
							{selectedModel.contextWindow && (
								<span className="rounded bg-muted px-1.5 py-px">{(selectedModel.contextWindow / 1000).toFixed(0)}k ctx</span>
							)}
							<span className="rounded bg-muted px-1.5 py-px">{formatCost(selectedModel.cost)}</span>
							{selectedModel.reasoning && <span className="rounded bg-emerald-500/10 text-emerald-600 px-1.5 py-px">reasoning</span>}
						</div>
					)}

					{/* Reasoning Effort Control */}
					{supportsReasoning && selectedModel?.thinkingLevelMap && (
						<div className="pt-1">
							<div className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wider mb-1.5">
								Reasoning Effort
							</div>
							<div className="flex flex-wrap gap-1">
								{REASONING_LEVELS.map((level) => {
									const available = selectedModel.thinkingLevelMap![level] !== undefined
									return (
										<button
											key={level}
											type="button"
											disabled={!available}
											onClick={() => setReasoningEffort(level as ReasoningEffort)}
											className={cn(
												'text-[10px] px-2 py-0.5 rounded border transition-colors',
												reasoningEffort === level
													? 'bg-primary text-primary-foreground border-primary'
													: 'hover:bg-muted border-border',
												!available && 'opacity-40 cursor-not-allowed'
											)}
										>
											{level}
										</button>
									)
								})}
							</div>
						</div>
					)}

					{selectedProviderKey && selectedModelId && (
						<Button size="sm" className="w-full h-7 text-xs mt-1" onClick={applySelection}>
							Use this model
						</Button>
					)}
				</div>
			)}

			{currentBaseURL && currentModel && (
				<div className="text-[10px] text-muted-foreground/70">
					Current: <span className="font-mono text-foreground/80">{currentModel}</span>
					{currentReasoningEffort && currentReasoningEffort !== 'off' && (
						<span className="ml-1 text-emerald-500/70">• {currentReasoningEffort}</span>
					)}
				</div>
			)}
		</div>
	)
}

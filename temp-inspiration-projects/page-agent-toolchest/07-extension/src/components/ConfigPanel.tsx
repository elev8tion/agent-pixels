import {
	Copy,
	CornerUpLeft,
	ExternalLink,
	Eye,
	EyeOff,
	FoldVertical,
	HatGlasses,
	Home,
	Loader2,
	Scale,
	UnfoldVertical,
} from 'lucide-react'
import { Logo } from '@/components/misc'
import { useEffect, useState } from 'react'
import { siGithub } from 'simple-icons'

import { DEMO_BASE_URL, DEMO_MODEL, isTestingEndpoint } from '@/agent/constants'
import type { ExtConfig, LanguagePreference } from '@/agent/useAgent'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { ModelPicker } from '@/components/ModelPicker'

interface ConfigPanelProps {
	config: ExtConfig | null
	onSave: (config: ExtConfig) => Promise<void>
	onClose: () => void
}

export function ConfigPanel({ config, onSave, onClose }: ConfigPanelProps) {
	const [baseURL, setBaseURL] = useState(config?.baseURL || DEMO_BASE_URL)
	const [model, setModel] = useState(config?.model || DEMO_MODEL)
	const [apiKey, setApiKey] = useState(config?.apiKey)
	const [language, setLanguage] = useState<LanguagePreference>(config?.language)
	const [maxSteps, setMaxSteps] = useState(config?.maxSteps)
	const [systemInstruction, setSystemInstruction] = useState(config?.systemInstruction ?? '')
	const [experimentalLlmsTxt, setExperimentalLlmsTxt] = useState(
		config?.experimentalLlmsTxt ?? false
	)
	const [experimentalIncludeAllTabs, setExperimentalIncludeAllTabs] = useState(
		config?.experimentalIncludeAllTabs ?? false
	)
	const [disableNamedToolChoice, setDisableNamedToolChoice] = useState(
		config?.disableNamedToolChoice ?? false
	)
	const [selectedReasoningEffort, setSelectedReasoningEffort] = useState<any>(config?.reasoningEffort ?? 'medium')
	const [advancedOpen, setAdvancedOpen] = useState(false)
	const [saving, setSaving] = useState(false)
	const [userAuthToken, setUserAuthToken] = useState('')
	const [copied, setCopied] = useState(false)
	const [showToken, setShowToken] = useState(false)
	const [showApiKey, setShowApiKey] = useState(false)

	const [prevConfig, setPrevConfig] = useState(config)
	if (prevConfig !== config) {
		setPrevConfig(config)
		setBaseURL(config?.baseURL || DEMO_BASE_URL)
		setModel(config?.model || DEMO_MODEL)
		setApiKey(config?.apiKey)
		setLanguage(config?.language)
		setMaxSteps(config?.maxSteps)
		setSystemInstruction(config?.systemInstruction ?? '')
		setExperimentalLlmsTxt(config?.experimentalLlmsTxt ?? false)
		setExperimentalIncludeAllTabs(config?.experimentalIncludeAllTabs ?? false)
		setDisableNamedToolChoice(config?.disableNamedToolChoice ?? false)
	}

	// Poll for user auth token every second until found
	useEffect(() => {
		let interval: NodeJS.Timeout | null = null

		const fetchToken = async () => {
			const result = await chrome.storage.local.get('PageAgentExtUserAuthToken')
			const token = result.PageAgentExtUserAuthToken
			if (typeof token === 'string' && token) {
				setUserAuthToken(token)
				if (interval) {
					clearInterval(interval)
					interval = null
				}
			}
		}

		fetchToken()
		interval = setInterval(fetchToken, 1000)

		return () => {
			if (interval) clearInterval(interval)
		}
	}, [])

	const handleCopyToken = async () => {
		if (userAuthToken) {
			await navigator.clipboard.writeText(userAuthToken)
			setCopied(true)
			setTimeout(() => setCopied(false), 2000)
		}
	}

	const handleSave = async () => {
		setSaving(true)
		try {
			await onSave({
				apiKey,
				baseURL,
				model,
				language,
				maxSteps: maxSteps || undefined,
				systemInstruction: systemInstruction || undefined,
				experimentalLlmsTxt,
				experimentalIncludeAllTabs,
				disableNamedToolChoice,
				reasoningEffort: selectedReasoningEffort,
			})
		} finally {
			setSaving(false)
		}
	}

	return (
		<div className="flex flex-col gap-4 p-4 relative text-[13px]">
			<div className="flex items-center justify-between -mx-1 px-1 py-1 rounded-[12px] bg-background/60 backdrop-blur border border-[var(--glass-border)]">
				<div className="flex items-center gap-2 ml-1.5">
					<Logo variant="letters" className="h-[15px] w-auto opacity-90" />
					<div>
						<h2 className="text-[15px] font-semibold tracking-[-0.2px]">Settings</h2>
						<p className="text-[10px] text-muted-foreground/60 -mt-0.5">Configure the model powering Agent Pixel</p>
					</div>
				</div>
				<Button
					variant="ghost"
					size="icon-sm"
					onClick={onClose}
					className="mr-1 cursor-pointer"
					aria-label="Back"
				>
					<CornerUpLeft className="size-3.5" />
				</Button>
			</div>

			{/* Pi Models - Professional discovery */}
			<div className="rounded-xl border bg-muted/10 p-3">
				<div className="flex items-baseline justify-between mb-2">
					<div className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">Your .pi Models</div>
					<div className="text-[9px] text-emerald-500/70">Connected to Pi</div>
				</div>
				<div className="text-[9px] text-muted-foreground/60 mb-1">
					Run <code className="font-mono text-[10px] bg-muted px-1 rounded">node scripts/sync-pi-models.js</code> in the extension folder for one-click sync.
				</div>
				<ModelPicker
					onSelect={(partial) => {
						if (partial.baseURL) setBaseURL(partial.baseURL)
						if (partial.model) setModel(partial.model)
						if (partial.reasoningEffort) setSelectedReasoningEffort(partial.reasoningEffort)
					}}
					currentBaseURL={baseURL}
					currentModel={model}
					currentReasoningEffort={selectedReasoningEffort}
				/>
			</div>

			{/* User Auth Token Section */}
			<div className="flex flex-col gap-1.5 p-3 glass bg-muted/30 rounded-xl border">
				<label htmlFor="user-auth-token" className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">
					User Auth Token
				</label>
				<p className="text-[10px] text-muted-foreground/70 mb-1">
					Give a website the ability to call this extension.
				</p>
				<div className="flex gap-2 items-center">
					<Input
						id="user-auth-token"
						readOnly
						value={
							userAuthToken
								? showToken
									? userAuthToken
									: `${userAuthToken.slice(0, 4)}${'•'.repeat(userAuthToken.length - 8)}${userAuthToken.slice(-4)}`
								: 'Loading...'
						}
						className="text-xs h-8 font-mono bg-background"
					/>
					<Button
						variant="outline"
						size="icon"
						className="h-8 w-8 shrink-0 cursor-pointer"
						onClick={() => setShowToken(!showToken)}
						disabled={!userAuthToken}
						aria-label={showToken ? 'Hide token' : 'Show token'}
						aria-pressed={showToken}
					>
						{showToken ? <EyeOff className="size-3" /> : <Eye className="size-3" />}
					</Button>
					<Button
						variant="outline"
						size="icon"
						className="h-8 w-8 shrink-0 cursor-pointer"
						onClick={handleCopyToken}
						disabled={!userAuthToken}
						aria-label="Copy token"
					>
						{copied ? <span className="">✓</span> : <Copy className="size-3" />}
					</Button>
					<span role="status" aria-live="polite" aria-atomic="true" className="sr-only">
						{copied ? 'Token copied' : ''}
					</span>
				</div>
			</div>

			{/* Hub link */}
			<a
				href="/hub.html"
				target="_blank"
				rel="noopener noreferrer"
				className="flex items-center justify-between p-3 rounded-xl border glass bg-muted/30 text-[12px] font-medium text-muted-foreground hover:text-foreground hover:border-[var(--glass-border)] transition-all"
			>
				Manage connected websites &amp; hub
				<ExternalLink className="size-3" />
			</a>

			<div className="flex flex-col gap-1.5">
				<label htmlFor="base-url" className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">
					Base URL
				</label>
				<Input
					id="base-url"
					placeholder="https://api.openai.com/v1"
					value={baseURL}
					onChange={(e) => setBaseURL(e.target.value)}
					className="text-xs h-8 font-mono"
				/>
				<div className="text-[9px] text-muted-foreground/60">From your .pi/models.json or any OpenAI-compatible server.</div>
			</div>

			{/* Testing API notice */}
			{isTestingEndpoint(baseURL) && (
				<div className="p-2.5 rounded-xl border border-[var(--accent-yellow)]/30 bg-[var(--accent-yellow)]/5 text-[11px] text-muted-foreground leading-relaxed">
					<Scale className="size-3 inline-block mr-1 -mt-0.5 text-amber-600" />
					You are using our testing API. By using this you agree to the{' '}
					<a
						href="https://github.com/alibaba/page-agent/blob/main/docs/terms-and-privacy.md"
						target="_blank"
						rel="noopener noreferrer"
						className="underline hover:text-foreground"
					>
						Terms of Use & Privacy Policy
					</a>
				</div>
			)}

			<div className="flex flex-col gap-1.5">
				<label htmlFor="model" className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">
					Model ID
				</label>
				<Input
					id="model"
					placeholder="qwen3.5-plus or deepseek-v4-pro"
					value={model}
					onChange={(e) => setModel(e.target.value)}
					className="text-xs h-8 font-mono"
				/>
				<div className="text-[9px] text-muted-foreground/60">Exact model identifier from the provider.</div>
			</div>

			<div className="flex flex-col gap-1.5">
				<label htmlFor="api-key" className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">
					API Key
				</label>
				<div className="flex gap-2 items-center">
					<Input
						id="api-key"
						type={showApiKey ? 'text' : 'password'}
						// placeholder="sk-..."
						value={apiKey}
						onChange={(e) => setApiKey(e.target.value)}
						className="text-xs h-8 font-mono"
					/>
					<Button
						variant="outline"
						size="icon"
						className="h-8 w-8 shrink-0 cursor-pointer"
						onClick={() => setShowApiKey(!showApiKey)}
						aria-label={showApiKey ? 'Hide API key' : 'Show API key'}
					>
						{showApiKey ? <EyeOff className="size-3" /> : <Eye className="size-3" />}
					</Button>
				</div>
				<div className="text-[9px] text-muted-foreground/60 -mt-1">$ENV_VAR references are resolved from your Pi environment.</div>
			</div>

			<div className="flex flex-col gap-1.5">
				<label className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">Response Language</label>
				<select
					value={language ?? ''}
					onChange={(e) => setLanguage((e.target.value || undefined) as LanguagePreference)}
					className="h-8 text-[12px] rounded-lg border border-input bg-background px-2 cursor-pointer"
				>
					<option value="">System</option>
					<option value="en-US">English</option>
					<option value="zh-CN">中文</option>
				</select>
			</div>

			{/* Advanced Config */}
			<button
				type="button"
				onClick={() => setAdvancedOpen(!advancedOpen)}
				className="flex items-center gap-1 text-[10px] font-medium text-muted-foreground hover:text-foreground cursor-pointer mt-2"
			>
				Advanced Options
				{advancedOpen ? <FoldVertical className="size-3" /> : <UnfoldVertical className="size-3" />}
			</button>

			{advancedOpen && (
				<>
					<div className="flex flex-col gap-1.5">
						<label htmlFor="max-steps" className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">
							Max Steps
						</label>
						<Input
							id="max-steps"
							type="number"
							placeholder="40"
							min={1}
							max={200}
							value={maxSteps ?? ''}
							onChange={(e) => setMaxSteps(e.target.value ? Number(e.target.value) : undefined)}
							className="text-xs h-8 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [-moz-appearance:textfield]"
						/>
					</div>

					<div className="flex flex-col gap-1.5">
						<label className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-[0.5px]">System Instruction</label>
						<textarea
							placeholder="Additional instructions for the agent..."
							value={systemInstruction}
							onChange={(e) => setSystemInstruction(e.target.value)}
							rows={3}
							className="text-xs rounded-md border border-input bg-background px-3 py-2 resize-y min-h-[60px]"
						/>
					</div>

					<label className="flex items-center justify-between cursor-pointer">
						<span className="text-[11px] text-muted-foreground">Disable named tool_choice</span>
						<Switch checked={disableNamedToolChoice} onCheckedChange={setDisableNamedToolChoice} />
					</label>

					<label className="flex items-center justify-between cursor-pointer">
						<span className="text-[11px] text-muted-foreground">Experimental llms.txt support</span>
						<Switch checked={experimentalLlmsTxt} onCheckedChange={setExperimentalLlmsTxt} />
					</label>

					<label className="flex items-center justify-between cursor-pointer">
						<span className="text-[11px] text-muted-foreground">Experimental include all tabs</span>
						<Switch
							checked={experimentalIncludeAllTabs}
							onCheckedChange={setExperimentalIncludeAllTabs}
						/>
					</label>
				</>
			)}

			<div className="flex gap-2 mt-2">
				<Button variant="outline" onClick={onClose} className="flex-1 h-8 text-xs cursor-pointer">
					Cancel
				</Button>
				<Button
					onClick={handleSave}
					disabled={saving}
					className="flex-1 h-8 text-xs cursor-pointer"
				>
					{saving ? <Loader2 className="size-3 animate-spin" /> : 'Save Configuration'}
				</Button>
			</div>

			{/* Footer */}
			<div className="mt-5 pt-4 border-t border-border/40 flex gap-2 justify-between text-[10px] text-muted-foreground/70">
				<div>
					<div>Version <span className="font-mono text-foreground/70">v{__VERSION__}</span></div>
					<a href="https://github.com/alibaba/page-agent" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-foreground mt-0.5">
						<svg role="img" viewBox="0 0 24 24" className="size-3 fill-current"><path d={siGithub.path} /></svg>
						<span>Source</span>
					</a>
				</div>
				<div className="text-right">
					<div className="flex justify-end gap-3">
						<a href="https://alibaba.github.io/page-agent/" target="_blank" className="hover:text-foreground inline-flex items-center gap-1"><Home className="size-3"/> Docs</a>
						<a href="https://github.com/alibaba/page-agent/blob/main/docs/terms-and-privacy.md" target="_blank" className="hover:text-foreground inline-flex items-center gap-1"><HatGlasses className="size-3"/> Privacy</a>
					</div>
				</div>
			</div>

			{/* attribute */}
			<div className="mt-6 pt-3 border-t border-border/40 text-[10px] text-muted-foreground/60 flex justify-center">
				<span>
					Built with ♥ by{' '}
					<a
						href="https://github.com/gaomeng1900"
						target="_blank"
						rel="noopener noreferrer"
						className="underline hover:text-foreground/80"
					>
						@Simon
					</a>
				</span>
			</div>
		</div>
	)
}

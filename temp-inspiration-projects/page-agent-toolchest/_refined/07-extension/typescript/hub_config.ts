function HubConfig() {
	const [allowAll, setAllowAll] = useState(false)

	useEffect(() => {
		chrome.storage.local.get('allowAllHubConnection').then((r) => {
			setAllowAll(r.allowAllHubConnection === true)
		})
	}, [])

	const toggle = (checked: boolean) => {
		setAllowAll(checked)
		chrome.storage.local.set({ allowAllHubConnection: checked })
	}

	return (
		<div>
			<h3 className="text-[11px] font-semibold text-foreground/80 uppercase tracking-wider mb-2">
				Config
			</h3>
			<div className="group/hub relative">
				<label
					className={`flex items-center justify-between p-3 rounded-md border cursor-pointer text-xs ${allowAll ? 'bg-amber-500/10 border-amber-500/30 text-amber-600' : 'bg-muted/50 text-muted-foreground'}`}
				>
					Auto-approve connections
					<Switch
						checked={allowAll}
						onCheckedChange={toggle}
						className={allowAll ? 'data-[state=checked]:bg-amber-500' : ''}
					/>
				</label>

				{/* hide with invisible absolute opacity-0*/}
				<div className="group-hover/hub:visible group-hover/hub:opacity-100 transition-opacity duration-150  left-0 right-0 top-full z-10 pt-2">
					<div className="relative p-2.5 rounded-md border border-border bg-background/60 backdrop-blur-md shadow-2xl text-muted-foreground text-xs leading-relaxed">
						<div className="absolute -top-1.5 left-5 size-3 rotate-45 rounded-[1px] border-l border-t border-border bg-background/60 backdrop-blur-md" />
						By default, each connection requires your approval before running tasks. <br />
						Enable this to skip per-session approval.
						<br />
						<span className="font-semibold">* Use with caution!</span>
					</div>
				</div>
			</div>
		</div>
	)
}

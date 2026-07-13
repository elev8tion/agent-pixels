export default function DocsPage() {
  const initialId = typeof window !== "undefined" ? window.location.hash.slice(1) : ""
  const [activeId, setActiveId] = React.useState<string>(
    endpoints.find((e) => e.id === initialId)?.id ?? "overview"
  )
  const active = endpoints.find((e) => e.id === activeId)

  function selectEndpoint(id: string) {
    setActiveId(id)
    window.history.replaceState(null, "", `#${id}`)
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-0 px-4 py-8 sm:px-6 md:flex-row md:py-10">
      {/* Sidebar */}
      <aside className="hidden w-56 shrink-0 pr-6 md:block">
        <nav className="mb-6 space-y-1">
          <button
            onClick={() => selectEndpoint("overview")}
            className={cn(
              "flex w-full items-center rounded-md px-2.5 py-1.5 text-left text-sm transition-colors",
              activeId === "overview"
                ? "bg-muted font-medium text-foreground"
                : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
            )}
          >
            Overview
          </button>
        </nav>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Endpoints
        </h2>
        <nav className="space-y-1">
          {endpoints.map((ep) => (
            <button
              key={ep.id}
              onClick={() => selectEndpoint(ep.id)}
              className={cn(
                "flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors",
                activeId === ep.id
                  ? "bg-muted font-medium text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              )}
            >
              <MethodBadge method={ep.method} />
              <span className="truncate font-mono text-xs">{ep.path}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Mobile endpoint selector */}
      <div className="mb-6 md:hidden">
        <select
          value={activeId}
          onChange={(e) => selectEndpoint(e.target.value)}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="overview">Overview</option>
          {endpoints.map((ep) => (
            <option key={ep.id} value={ep.id}>
              {ep.method} {ep.path}
            </option>
          ))}
        </select>
      </div>

      {/* Main content */}
      <div className="min-w-0 flex-1">
        {active ? (
          <>
            <div className="flex items-center gap-3">
              <MethodBadge method={active.method} />
              <h1 className="font-mono text-lg font-semibold">{active.path}</h1>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{active.summary}</p>

            <div className="mt-6 space-y-6">
              {/* Description */}
              <p className="text-sm leading-relaxed text-foreground/80">
                {active.description}
              </p>

              {/* Try it — most useful, put first */}
              <ApiPlayground
                key={active.id}
                method={active.method}
                path={active.path}
                curlPrefix={active.curlPrefix}
                defaultBody={active.defaultBody}
                defaultParams={active.defaultParams}
                buildPath={active.buildPath}
              />

              {/* Schema — Request + Response side by side when both exist */}
              {active.requestFields ? (
                <div className="grid gap-4 lg:grid-cols-2">
                  <Section title="Request">
                    <FieldTable fields={active.requestFields} />
                  </Section>
                  {active.responseFields && (
                    <Section title="Response">
                      <FieldTable fields={active.responseFields} />
                    </Section>
                  )}
                </div>
              ) : active.responseFields ? (
                <Section title="Response">
                  <FieldTable fields={active.responseFields} />
                </Section>
              ) : null}
            </div>
          </>
        ) : (
          <OverviewSection onSelect={selectEndpoint} />
        )}
      </div>
    </div>
  )
}

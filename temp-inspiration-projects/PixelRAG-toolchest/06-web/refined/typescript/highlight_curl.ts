function highlightCurl(curl: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const regex = /\b(curl)\b|(-[XHIG]|--\w[\w-]*)|("(?:[^"\\]|\\.)*")|'([^']*)'|(https?:\/\/\S+)|(\\\n\s*)|(\s+)/g
  let match: RegExpExecArray | null
  let lastIndex = 0
  let key = 0
  while ((match = regex.exec(curl)) !== null) {
    if (match.index > lastIndex)
      nodes.push(<span key={key++} className="text-foreground/40">{curl.slice(lastIndex, match.index)}</span>)
    lastIndex = match.index + match[0].length
    if (match[1]) {
      nodes.push(<span key={key++} className="text-green-400">{match[1]}</span>)
    } else if (match[2]) {
      nodes.push(<span key={key++} className="text-amber-400">{match[2]}</span>)
    } else if (match[3]) {
      nodes.push(<span key={key++} className="text-purple-400">{match[3]}</span>)
    } else if (match[4] !== undefined) {
      nodes.push(<span key={key++} className="text-foreground/40">{"'"}</span>)
      nodes.push(<span key={key++} className="text-green-400/70">{match[4]}</span>)
      nodes.push(<span key={key++} className="text-foreground/40">{"'"}</span>)
    } else if (match[5]) {
      nodes.push(<span key={key++} className="text-cyan-400">{match[5]}</span>)
    } else {
      nodes.push(<span key={key++} className="text-foreground/30">{match[0]}</span>)
    }
  }
  if (lastIndex < curl.length)
    nodes.push(<span key={key++} className="text-foreground/40">{curl.slice(lastIndex)}</span>)
  return nodes
}

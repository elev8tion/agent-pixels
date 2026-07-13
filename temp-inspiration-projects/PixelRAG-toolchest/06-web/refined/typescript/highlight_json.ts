function highlightJson(code: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const regex = /("(?:[^"\\]|\\.)*")(\s*:)?|(\b(?:true|false|null)\b)|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}[\],:])|(\s+)/g
  let match: RegExpExecArray | null
  let lastIndex = 0
  let key = 0
  while ((match = regex.exec(code)) !== null) {
    if (match.index > lastIndex)
      nodes.push(<span key={key++} className="text-foreground/50">{code.slice(lastIndex, match.index)}</span>)
    lastIndex = match.index + match[0].length
    if (match[1] !== undefined) {
      if (match[2] !== undefined) {
        nodes.push(<span key={key++} className="text-foreground/90">{match[1]}</span>)
        nodes.push(<span key={key++} className="text-foreground/30">{match[2]}</span>)
      } else {
        nodes.push(<span key={key++} className="text-green-400">{match[1]}</span>)
      }
    } else if (match[3] !== undefined) {
      nodes.push(<span key={key++} className="text-amber-400">{match[3]}</span>)
    } else if (match[4] !== undefined) {
      nodes.push(<span key={key++} className="text-blue-400">{match[4]}</span>)
    } else if (match[5] !== undefined) {
      nodes.push(<span key={key++} className="text-foreground/25">{match[5]}</span>)
    } else if (match[6] !== undefined) {
      nodes.push(match[6])
    }
  }
  if (lastIndex < code.length)
    nodes.push(<span key={key++} className="text-foreground/50">{code.slice(lastIndex)}</span>)
  return nodes
}

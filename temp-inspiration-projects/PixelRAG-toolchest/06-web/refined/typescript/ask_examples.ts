const ASK_EXAMPLES = [
  "How many shots on target did Inter have in the 2010 Champions League final?",
  "Which district in Nagaland has the RTO code NL-03?",
  "Explain Van Gogh's The Starry Night",
  "介绍一下兵马俑",
]

interface SearchBarProps {
  onSearch: (query: string, image?: string) => void
  onReset?: () => void
  isLoading: boolean
  hasResults?: boolean
  defaultValue?: string
  mode?: "search" | "ask"
}

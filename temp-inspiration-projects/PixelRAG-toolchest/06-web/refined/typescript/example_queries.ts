const EXAMPLE_QUERIES = [
  "The Starry Night",
  "Periodic table",
  "Taj Mahal",
  "The Great Wave off Kanagawa",
  "清明上河图",
]

// The first two are verified "ChatGPT gets these wrong" questions: the answers
// live in table/infobox cells (match-stats table, RTO code box) that parametric
// memory and text scraping both fumble — but reading the rendered page nails.
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

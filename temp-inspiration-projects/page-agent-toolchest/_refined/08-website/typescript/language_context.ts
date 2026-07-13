const LanguageContext = createContext<{
	language: Lang
	isZh: boolean
	setLanguage: (lang: Lang) => void
} | null>(null)

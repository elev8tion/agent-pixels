const CodeEditor: React.FC<CodeEditorProps> = ({
	code,
	language = 'javascript',
	title,
	showLineNumbers = false,
	showHeader = false,
	showFooter = false,
	className = '',
}) => {

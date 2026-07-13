export const getAllTextTillNextClickableElement = (node: TreeNode, maxDepth = -1): string => {
	const textParts: string[] = []

	const collectText = (currentNode: TreeNode, currentDepth: number) => {
		if (maxDepth !== -1 && currentDepth > maxDepth) {
			return
		}

		// Skip this branch if we hit a highlighted element (except for the current node)
		if (
			currentNode.type === 'element' &&
			currentNode !== node &&
			currentNode.highlightIndex !== undefined
		) {
			return
		}

		if (currentNode.type === 'text' && currentNode.text) {
			textParts.push(currentNode.text)
		} else if (currentNode.type === 'element') {
			for (const child of currentNode.children) {
				collectText(child, currentDepth + 1)
			}
		}
	}

	collectText(node, 0)
	return textParts.join('\n').trim()
}

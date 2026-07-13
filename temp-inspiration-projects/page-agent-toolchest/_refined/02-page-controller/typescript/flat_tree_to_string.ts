export function flatTreeToString(
	flatTree: FlatDomTree,
	includeAttributes: string[] = [],
	keepSemanticTags = false
): string {
	const DEFAULT_INCLUDE_ATTRIBUTES = [
		'title',
		'type',
		'checked',
		'name',
		'role',
		'value',
		'placeholder',
		'data-date-format',
		'alt',
		'aria-label',
		'aria-expanded',
		'data-state',
		'aria-checked',

		// @edit added for better form handling
		'id',
		'for',

		// for jump check
		'target',

		// absolute position dropdown menu
		'aria-haspopup',
		'aria-controls',
		'aria-owns',

		// content editable
		'contenteditable',
	]

	const includeAttrs = [...includeAttributes, ...DEFAULT_INCLUDE_ATTRIBUTES]

	// Helper function to cap text length
	const capTextLength = (text: string, maxLength: number): string => {
		if (text.length > maxLength) {
			return text.substring(0, maxLength) + '...'
		}
		return text
	}

	// Build tree structure from flat map
	const buildTreeNode = (nodeId: string): TreeNode | null => {
		const node = flatTree.map[nodeId]
		if (!node) return null

		if (node.type === 'TEXT_NODE') {
			const textNode = node as TextDomNode
			return {
				type: 'text',
				text: textNode.text,
				isVisible: textNode.isVisible,
				parent: null,
				children: [],
			}
		} else {
			const elementNode = node as ElementDomNode
			const children: TreeNode[] = []

			if (elementNode.children) {
				for (const childId of elementNode.children) {
					const child = buildTreeNode(childId)
					if (child) {
						child.parent = null // Will be set later
						children.push(child)
					}
				}
			}

			return {
				type: 'element',
				tagName: elementNode.tagName,
				attributes: elementNode.attributes ?? {},
				isVisible: elementNode.isVisible ?? false,
				isInteractive: elementNode.isInteractive ?? false,
				isTopElement: elementNode.isTopElement ?? false,
				isNew: elementNode.isNew ?? false,
				highlightIndex: elementNode.highlightIndex,
				parent: null,
				children,
				extra: elementNode.extra ?? {},
			}
		}
	}

	// Set parent references
	const setParentReferences = (node: TreeNode, parent: TreeNode | null = null) => {
		node.parent = parent
		for (const child of node.children) {
			setParentReferences(child, node)
		}
	}

	// Build root node
	const rootNode = buildTreeNode(flatTree.rootId)
	if (!rootNode) return ''

	setParentReferences(rootNode)

	// Helper to check if text node has parent with highlight index
	const hasParentWithHighlightIndex = (node: TreeNode): boolean => {
		let current = node.parent
		while (current) {
			if (current.type === 'element' && current.highlightIndex !== undefined) {
				return true
			}
			current = current.parent
		}
		return false
	}

	// Helper to check if parent is top element
	// const isParentTopElement = (node: TreeNode): boolean => {
	// 	return node.parent?.type === 'element' && node.parent.isTopElement === true
	// }

	// Main processing function
	const processNode = (node: TreeNode, depth: number, result: string[]): void => {
		let nextDepth = depth
		const depthStr = '\t'.repeat(depth)

		if (node.type === 'element') {
			const isSemantic = keepSemanticTags && node.tagName && SEMANTIC_TAGS.has(node.tagName)

			// Add element with highlight_index
			if (node.highlightIndex !== undefined) {
				nextDepth += 1

				const text = getAllTextTillNextClickableElement(node)
				let attributesHtmlStr = ''

				if (includeAttrs.length > 0 && node.attributes) {
					const attributesToInclude = matchAttributes(node.attributes, includeAttrs)

					// Remove duplicate values (for attributes longer than 5 chars)
					const keys = Object.keys(attributesToInclude)
					if (keys.length > 1) {
						const keysToRemove = new Set<string>()
						const seenValues: Record<string, string> = {}

						for (const key of keys) {
							const value = attributesToInclude[key]
							if (value.length > 5) {
								if (value in seenValues) {
									keysToRemove.add(key)
								} else {
									seenValues[value] = key
								}
							}
						}

						for (const key of keysToRemove) {
							delete attributesToInclude[key]
						}
					}

					// Remove role if it matches tagName
					if (attributesToInclude.role === node.tagName) {
						delete attributesToInclude.role
					}

					// Remove attributes that duplicate text content
					const attrsToRemoveIfTextMatches = ['aria-label', 'placeholder', 'title']
					for (const attr of attrsToRemoveIfTextMatches) {
						if (
							attributesToInclude[attr] &&
							attributesToInclude[attr].toLowerCase().trim() === text.toLowerCase().trim()
						) {
							delete attributesToInclude[attr]
						}
					}

					if (Object.keys(attributesToInclude).length > 0) {
						attributesHtmlStr = Object.entries(attributesToInclude)
							.map(([key, value]) => `${key}=${capTextLength(value, 20)}`)
							.join(' ')
					}
				}

				// Build the line
				const highlightIndicator = node.isNew
					? `*[${node.highlightIndex}]`
					: `[${node.highlightIndex}]`
				let line = `${depthStr}${highlightIndicator}<${node.tagName ?? ''}`

				if (attributesHtmlStr) {
					line += ` ${attributesHtmlStr}`
				}

				/**
				 * @edit scrollable 数据
				 */
				if (node.extra) {
					if (node.extra.scrollable) {
						let scrollDataText = ''
						if (node.extra.scrollData?.left)
							scrollDataText += `left=${node.extra.scrollData.left}, `
						if (node.extra.scrollData?.top) scrollDataText += `top=${node.extra.scrollData.top}, `
						if (node.extra.scrollData?.right)
							scrollDataText += `right=${node.extra.scrollData.right}, `
						if (node.extra.scrollData?.bottom)
							scrollDataText += `bottom=${node.extra.scrollData.bottom}`

						line += ` data-scrollable="${scrollDataText}"`
					}
				}

				if (text) {
					const trimmedText = text.trim()
					if (!attributesHtmlStr) {
						line += ' '
					}
					line += `>${trimmedText}`
				} else if (!attributesHtmlStr) {
					line += ' '
				}

				line += ' />'
				result.push(line)
			}

			// special treatment for semantic tags
			// even if they are not interactive, we can keep them for clear context

			const emitSemantic = isSemantic && node.highlightIndex === undefined
			// to check if this tag is empty
			const mark = emitSemantic ? result.length : -1

			if (emitSemantic) {
				result.push(`${depthStr}<${node.tagName}>`)
				nextDepth += 1
			}

			for (const child of node.children) {
				processNode(child, nextDepth, result)
			}

			if (emitSemantic) {
				// empty tag should be removed
				if (result.length === mark + 1) {
					result.pop()
				} else {
					result.push(`${depthStr}</${node.tagName}>`)
				}
			}
		} else if (node.type === 'text') {
			// Add text only if it doesn't have a highlighted parent
			if (hasParentWithHighlightIndex(node)) {
				return
			}

			if (
				node.parent &&
				node.parent.type === 'element' &&
				node.parent.isVisible &&
				node.parent.isTopElement
			) {
				result.push(`${depthStr}${node.text ?? ''}`)
			}
		}
	}

	const result: string[] = []
	processNode(rootNode, 0, result)
	return result.join('\n')
}

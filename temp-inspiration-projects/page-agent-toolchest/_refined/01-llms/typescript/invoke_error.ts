export class InvokeError extends Error {
	type: InvokeErrorType
	retryable: boolean
	statusCode?: number
	/* raw error (provided if this error is caused by another error) */
	rawError?: unknown
	/* raw response from the API (provided if this error is caused by an API calling) */
	rawResponse?: unknown

	constructor(type: InvokeErrorType, message: string, rawError?: unknown, rawResponse?: unknown) {
		super(message)
		this.name = 'InvokeError'
		this.type = type
		this.retryable = RETRYABLE_TYPES.includes(type)
		this.rawError = rawError
		this.rawResponse = rawResponse
	}
}

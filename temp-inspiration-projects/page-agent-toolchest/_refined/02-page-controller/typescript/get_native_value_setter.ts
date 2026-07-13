export function getNativeValueSetter(element: HTMLInputElement | HTMLTextAreaElement) {
-next-line @typescript-eslint/unbound-method
	return Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element) as object, 'value')!
		.set as (v: string) => void
}

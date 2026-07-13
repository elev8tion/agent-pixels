export async function clickPointer() {
	window.dispatchEvent(new CustomEvent('PageAgent::ClickPointer'))
}

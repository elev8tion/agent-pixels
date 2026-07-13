export async function enablePassThrough() {
	window.dispatchEvent(new CustomEvent('PageAgent::EnablePassThrough'))
}

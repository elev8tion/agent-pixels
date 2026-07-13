export async function disablePassThrough() {
	window.dispatchEvent(new CustomEvent('PageAgent::DisablePassThrough'))
}

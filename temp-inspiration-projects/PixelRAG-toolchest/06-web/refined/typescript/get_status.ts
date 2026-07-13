export async function getStatus(): Promise<StatusResponse> {
  return fetchApi<StatusResponse>("/status");
}

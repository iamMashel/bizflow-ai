type ApiClientOptions = {
  baseUrl?: string;
  fetcher?: typeof fetch;
};

export class ApiClient {
  private readonly baseUrl: string;
  private readonly fetcher: typeof fetch;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "";
    this.fetcher = options.fetcher ?? fetch;
  }

  async request<TResponse>(path: string, init?: RequestInit): Promise<TResponse> {
    if (!this.baseUrl) {
      throw new Error("NEXT_PUBLIC_API_URL is not configured.");
    }

    const response = await this.fetcher(new URL(path, this.baseUrl), {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}.`);
    }

    return (await response.json()) as TResponse;
  }
}

export const apiClient = new ApiClient();

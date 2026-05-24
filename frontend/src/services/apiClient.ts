import axios, { AxiosError } from 'axios';

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

interface FilterOptions {
  [key: string]: string | number | boolean | undefined;
}

interface SortOptions {
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export class ApiClient {
  private baseURL: string;

  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
  }

  private getHeaders(): Record<string, string> {
    const token = localStorage.getItem('authToken');
    return {
      Authorization: token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    };
  }

  async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    params?: FilterOptions & SortOptions
  ): Promise<T> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await axios({
        method,
        url,
        data,
        params,
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new ApiError(
          error.response?.status || 500,
          error.response?.data?.message || 'API request failed',
          error.response?.data
        );
      }
      throw error;
    }
  }

  async get<T>(endpoint: string, params?: FilterOptions & SortOptions): Promise<T> {
    return this.request<T>('GET', endpoint, undefined, params);
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }

  async getPaginated<T>(
    endpoint: string,
    page: number,
    pageSize: number,
    filters?: FilterOptions,
    sort?: SortOptions
  ): Promise<PaginatedResponse<T>> {
    const params = {
      ...filters,
      ...sort,
      page,
      pageSize,
    };
    return this.get<PaginatedResponse<T>>(endpoint, params);
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = new ApiClient();

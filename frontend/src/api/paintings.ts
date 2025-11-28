import api from "./client";

export type Painting = {
  id: number;
  user_id: number;
  title: string;
  tags?: string;
  folder?: string;
  thumbnail_url?: string;
  image_url?: string;
  width?: number;
  height?: number;
  format?: string;
  created_at: string;
  updated_at: string;
};

export type PaginatedPaintings = {
  items: Painting[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};

export const fetchPaintings = async (params: Record<string, unknown>) => {
  const { data } = await api.get<PaginatedPaintings>("/api/paintings", {
    params
  });
  return data;
};

export const fetchPainting = async (id: string) => {
  const { data } = await api.get<Painting>(`/api/paintings/${id}`);
  return data;
};

export const createPainting = async (payload: FormData) => {
  const { data } = await api.post<Painting>("/api/paintings", payload, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const updatePainting = async (id: string, payload: FormData | object) => {
  const formData = payload instanceof FormData;
  const { data } = await api.put<Painting>(
    `/api/paintings/${id}`,
    payload,
    {
      headers: formData ? { "Content-Type": "multipart/form-data" } : undefined
    }
  );
  return data;
};

export const importRemoteImage = async (payload: { image_url: string; format?: string }) => {
  const { data } = await api.post<{
    data_url: string;
    width: number;
    height: number;
    format: string;
  }>("/api/paintings/import-url", payload);
  return data;
};


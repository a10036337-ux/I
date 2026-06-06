import axios from 'axios';
import type { Interval, KBar, OrderPayload, WatchlistItem } from '../types/trading';

export const api = axios.create({ baseURL: '' });

export async function login(apiKey: string, secretKey: string) {
  const { data } = await api.post('/api/login', { api_key: apiKey, secret_key: secretKey });
  return data;
}

export async function fetchKbars(symbol: string, interval: Interval): Promise<KBar[]> {
  const end = new Date();
  const start = new Date();
  start.setMonth(start.getMonth() - 6);
  const { data } = await api.get('/api/kbars', {
    params: { symbol, interval, start: start.toISOString(), end: end.toISOString() }
  });
  return data;
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await api.get('/api/watchlist');
  return data;
}

export async function addWatchlist(symbol: string, name = ''): Promise<WatchlistItem> {
  const { data } = await api.post('/api/watchlist', { symbol, name, group_name: 'Default', sort_order: 0 });
  return data;
}

export async function placeOrder(payload: OrderPayload) {
  const { data } = await api.post('/api/order', payload);
  return data;
}

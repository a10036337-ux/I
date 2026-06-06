export type Interval = '1d' | '60m' | '30m' | '15m' | '5m' | '1m';
export type Action = 'buy' | 'sell';
export type PriceType = 'market' | 'limit';
export type OrderType = 'ROD' | 'IOC' | 'FOK';

export interface KBar {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TickMessage {
  type: 'tick';
  symbol: string;
  datetime: string;
  price: number;
  volume: number;
  change_percent: number;
  bidask: {
    bids: [number, number][];
    asks: [number, number][];
  };
}

export interface WatchlistItem {
  id: number;
  symbol: string;
  name: string;
  group_name: string;
  sort_order: number;
}

export interface OrderPayload {
  symbol: string;
  action: Action;
  price?: number;
  quantity: number;
  price_type: PriceType;
  order_type: OrderType;
  security_type: 'stock' | 'future';
}

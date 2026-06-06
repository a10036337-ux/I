import { Button, Card, Input, List, Space, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { addWatchlist, fetchWatchlist } from '../services/api';
import type { WatchlistItem } from '../types/trading';

interface Props {
  selected: string;
  onSelect: (symbol: string) => void;
}

export function Watchlist({ selected, onSelect }: Props) {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [symbol, setSymbol] = useState('2330');

  useEffect(() => { fetchWatchlist().then(setItems); }, []);

  return (
    <Card title="自選股" className="panel-card watchlist">
      <Space.Compact style={{ width: '100%', marginBottom: 12 }}>
        <Input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
        <Button onClick={async () => setItems([...items, await addWatchlist(symbol)])}>新增</Button>
      </Space.Compact>
      <List dataSource={items.length ? items : [{ id: 0, symbol: '2330', name: '台積電', group_name: 'Default', sort_order: 0 }]}
        renderItem={(item) => (
          <List.Item onClick={() => onSelect(item.symbol)} className={selected === item.symbol ? 'selected-row' : ''}>
            <Space><Tag>{item.group_name}</Tag><b>{item.symbol}</b><span>{item.name}</span></Space>
          </List.Item>
        )}
      />
    </Card>
  );
}

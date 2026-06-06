import { Card, Table, Tag } from 'antd';
import { useEffect, useState } from 'react';
import type { TickMessage } from '../types/trading';

interface Props { symbol: string; }

export function MarketTape({ symbol }: Props) {
  const [ticks, setTicks] = useState<TickMessage[]>([]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/market`);
    ws.onopen = () => ws.send(JSON.stringify({ type: 'subscribe', symbol }));
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data) as TickMessage;
      if (payload.symbol === symbol) setTicks((prev) => [payload, ...prev].slice(0, 30));
    };
    return () => ws.close();
  }, [symbol]);

  return (
    <Card title="成交明細 / 即時損益來源" className="panel-card tape-card">
      <Table size="small" pagination={false} dataSource={ticks} rowKey={(row) => row.datetime}
        columns={[
          { title: '時間', dataIndex: 'datetime', render: (value) => value.slice(11, 19) },
          { title: '成交價', dataIndex: 'price' },
          { title: '量', dataIndex: 'volume' },
          { title: '漲跌幅', dataIndex: 'change_percent', render: (value) => <Tag color={value >= 0 ? 'red' : 'green'}>{value}%</Tag> }
        ]}
      />
    </Card>
  );
}

import { Layout, Typography } from 'antd';
import { useState } from 'react';
import { ChartPanel } from './components/ChartPanel';
import { LoginPanel } from './components/LoginPanel';
import { MarketTape } from './components/MarketTape';
import { OrderPanel } from './components/OrderPanel';
import { Watchlist } from './components/Watchlist';
import type { Interval } from './types/trading';
import './styles.css';

export default function App() {
  const [symbol, setSymbol] = useState('2330');
  const [interval, setInterval] = useState<Interval>('1d');
  const [account, setAccount] = useState('未登入');

  return (
    <Layout className="app-shell">
      <Layout.Header className="app-header">
        <Typography.Title level={3}>台股專業量化交易系統</Typography.Title>
        <span>帳號：{account}</span>
      </Layout.Header>
      <Layout className="workspace">
        <Layout.Sider width={280} className="left-pane"><Watchlist selected={symbol} onSelect={setSymbol} /></Layout.Sider>
        <Layout.Content className="center-pane">
          <ChartPanel symbol={symbol} interval={interval} onIntervalChange={setInterval} />
          <MarketTape symbol={symbol} />
        </Layout.Content>
        <Layout.Sider width={340} className="right-pane">
          <LoginPanel onLogin={setAccount} />
          <OrderPanel symbol={symbol} />
        </Layout.Sider>
      </Layout>
    </Layout>
  );
}

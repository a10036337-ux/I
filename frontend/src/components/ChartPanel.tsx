import { Card, Segmented } from 'antd';
import { CandlestickSeries, HistogramSeries, createChart } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { fetchKbars } from '../services/api';
import type { Interval } from '../types/trading';

interface Props {
  symbol: string;
  interval: Interval;
  onIntervalChange: (interval: Interval) => void;
}

export function ChartPanel({ symbol, interval, onIntervalChange }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.innerHTML = '';
    const chart = createChart(ref.current, {
      height: 540,
      layout: { background: { color: '#0f172a' }, textColor: '#cbd5e1' },
      grid: { vertLines: { color: '#1e293b' }, horzLines: { color: '#1e293b' } },
      crosshair: { mode: 1 },
      rightPriceScale: { borderColor: '#334155' },
      timeScale: { borderColor: '#334155' }
    });
    const candle = chart.addSeries(CandlestickSeries, { upColor: '#ef4444', downColor: '#22c55e', borderVisible: false });
    const volume = chart.addSeries(HistogramSeries, { priceFormat: { type: 'volume' }, priceScaleId: '' });
    volume.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    fetchKbars(symbol, interval).then((rows) => {
      candle.setData(rows.map((row) => ({ time: row.datetime.slice(0, 10), open: row.open, high: row.high, low: row.low, close: row.close })));
      volume.setData(rows.map((row) => ({ time: row.datetime.slice(0, 10), value: row.volume, color: row.close >= row.open ? '#ef444480' : '#22c55e80' })));
      chart.timeScale().fitContent();
    });
    return () => chart.remove();
  }, [symbol, interval]);

  return (
    <Card title={`${symbol} K線圖`} extra={<Segmented value={interval} options={['1d', '60m', '5m']} onChange={(value) => onIntervalChange(value as Interval)} />} className="panel-card chart-card">
      <div ref={ref} />
      <div className="indicator-strip">MA｜EMA｜BBANDS｜RSI｜MACD｜KD 指標由後端計算，可擴充疊加至圖表。</div>
    </Card>
  );
}

import { Button, Card, Form, InputNumber, Radio, Select, Typography } from 'antd';
import { placeOrder } from '../services/api';
import type { OrderPayload } from '../types/trading';

interface Props { symbol: string; }

export function OrderPanel({ symbol }: Props) {
  return (
    <Card title="下單面板" className="panel-card">
      <Form layout="vertical" initialValues={{ action: 'buy', quantity: 1000, price_type: 'limit', order_type: 'ROD', security_type: 'stock' }}
        onFinish={async (values) => {
          const payload: OrderPayload = { ...values, symbol };
          const result = await placeOrder(payload);
          window.alert(`${result.status}: ${result.order_id}`);
        }}>
        <Typography.Title level={4}>{symbol}</Typography.Title>
        <Form.Item name="security_type" label="商品"><Select options={[{ value: 'stock', label: '股票' }, { value: 'future', label: '期貨' }]} /></Form.Item>
        <Form.Item name="action" label="買賣"><Radio.Group options={[{ value: 'buy', label: '買進' }, { value: 'sell', label: '賣出' }]} /></Form.Item>
        <Form.Item name="price_type" label="價格類型"><Radio.Group options={[{ value: 'market', label: '市價' }, { value: 'limit', label: '限價' }]} /></Form.Item>
        <Form.Item name="price" label="價格"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
        <Form.Item name="quantity" label="數量"><InputNumber style={{ width: '100%' }} min={1} step={1000} /></Form.Item>
        <Form.Item name="order_type" label="委託條件"><Select options={['ROD', 'IOC', 'FOK'].map((value) => ({ value, label: value }))} /></Form.Item>
        <Button type="primary" htmlType="submit" block>送出委託</Button>
      </Form>
    </Card>
  );
}

import { Button, Card, Form, Input, Typography } from 'antd';
import { useState } from 'react';
import { login } from '../services/api';

interface Props {
  onLogin: (account: string) => void;
}

export function LoginPanel({ onLogin }: Props) {
  const [status, setStatus] = useState('尚未登入');

  return (
    <Card title="永豐 API 登入" className="panel-card">
      <Form layout="vertical" onFinish={async (values) => {
        const result = await login(values.apiKey, values.secretKey);
        setStatus(`帳號 ${result.account}｜股票 ${result.stock_account ?? '-'}｜期貨 ${result.future_account ?? '-'}`);
        onLogin(result.account);
      }}>
        <Form.Item name="apiKey" label="API_KEY" rules={[{ required: true }]}>
          <Input.Password placeholder="輸入 API KEY" />
        </Form.Item>
        <Form.Item name="secretKey" label="SECRET_KEY" rules={[{ required: true }]}>
          <Input.Password placeholder="輸入 SECRET KEY" />
        </Form.Item>
        <Button type="primary" htmlType="submit" block>登入</Button>
      </Form>
      <Typography.Text type="secondary">{status}</Typography.Text>
    </Card>
  );
}

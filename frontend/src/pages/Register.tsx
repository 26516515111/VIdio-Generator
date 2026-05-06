import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { register } from '../store/authSlice';
import type { RootState, AppDispatch } from '../store';

const Register: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const onFinish = async (values: { username: string; email: string; password: string }) => {
    const result = await dispatch(register(values));
    if (register.fulfilled.match(result)) {
      message.success('注册成功，请登录');
      navigate('/login');
    }
  };

  return (
    <Card title="注册" style={{ maxWidth: 400, margin: '100px auto' }}>
      {error && (
        <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>
      )}
      <Form onFinish={onFinish}>
        <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
          <Input prefix={<UserOutlined />} placeholder="用户名" />
        </Form.Item>
        <Form.Item name="email" rules={[{ required: true, type: 'email', message: '请输入有效邮箱' }]}>
          <Input prefix={<MailOutlined />} placeholder="邮箱" />
        </Form.Item>
        <Form.Item name="password" rules={[{ required: true, min: 6, message: '密码至少6位' }]}>
          <Input.Password prefix={<LockOutlined />} placeholder="密码" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            注册
          </Button>
        </Form.Item>
        <Form.Item>
          <Button type="link" onClick={() => navigate('/login')} block>
            已有账号？立即登录
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Register;

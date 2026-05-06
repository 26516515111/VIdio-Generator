import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, message, List, Tag, Popconfirm } from 'antd';
import { UserOutlined, KeyOutlined, DeleteOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import api from '../services/api';

const { Option } = Select;

interface ApiKey {
  id: number;
  service_type: string;
  provider: string;
  is_default: boolean;
}

const Profile: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await api.get('/users/api-keys');
      setApiKeys(response.data);
    } catch (error) {
      message.error('获取API密钥失败');
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await api.post('/users/api-keys', values);
      message.success('API密钥添加成功');
      form.resetFields();
      fetchApiKeys();
    } catch (error) {
      message.error('添加API密钥失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/users/api-keys/${id}`);
      message.success('API密钥删除成功');
      fetchApiKeys();
    } catch (error) {
      message.error('删除API密钥失败');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Card title="个人信息" style={{ marginBottom: 24 }}>
        <p>
          <UserOutlined /> 用户名：{user?.username}
        </p>
        <p>邮箱：{user?.email}</p>
      </Card>

      <Card title="API密钥管理">
        <Form form={form} onFinish={onFinish} layout="vertical">
          <Form.Item
            name="service_type"
            label="服务类型"
            rules={[{ required: true, message: '请选择服务类型' }]}
          >
            <Select placeholder="选择服务类型">
              <Option value="ocr">OCR服务</Option>
              <Option value="llm">大语言模型</Option>
              <Option value="tts">TTS服务</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="provider"
            label="服务提供商"
            rules={[{ required: true, message: '请选择服务提供商' }]}
          >
            <Select placeholder="选择服务提供商">
              <Option value="xiaomi">小米</Option>
              <Option value="openai">OpenAI</Option>
              <Option value="baidu">百度</Option>
              <Option value="tencent">腾讯</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="api_key"
            label="API密钥"
            rules={[{ required: true, message: '请输入API密钥' }]}
          >
            <Input.Password prefix={<KeyOutlined />} placeholder="输入API密钥" />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认" initialValue={false}>
            <Select>
              <Option value={true}>是</Option>
              <Option value={false}>否</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              添加密钥
            </Button>
          </Form.Item>
        </Form>

        <List
          header={<div>已添加的API密钥</div>}
          dataSource={apiKeys}
          locale={{ emptyText: '暂无API密钥' }}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Popconfirm
                  title="确定删除此API密钥？"
                  onConfirm={() => handleDelete(item.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="link" danger icon={<DeleteOutlined />} />
                </Popconfirm>,
              ]}
            >
              <Tag color={item.is_default ? 'green' : 'default'}>
                {item.service_type.toUpperCase()}
              </Tag>
              <span>{item.provider}</span>
              {item.is_default && (
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  默认
                </Tag>
              )}
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Profile;

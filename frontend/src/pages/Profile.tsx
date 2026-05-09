import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, Switch, message, List, Tag, Popconfirm, Space } from 'antd';
import { UserOutlined, KeyOutlined, DeleteOutlined, LinkOutlined, RobotOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import api from '../services/api';

const { Option } = Select;

interface ApiKey {
  id: number;
  service_type: string;
  provider: string;
  base_url: string | null;
  model_name: string | null;
  is_default: boolean;
}

// 每个提供商的默认模型（按服务类型区分）
const defaultModels: Record<string, Record<string, string>> = {
  'xiaomi-tokenplan': {
    ocr: 'mimo-v2.5',
    llm: 'mimo-v2.5-pro',
    tts: 'mimo-v2-tts',
  },
  xiaomi: {
    ocr: 'mimo-v2.5',
    llm: 'mimo-v2.5-pro',
    tts: 'mimo-v2-tts',
  },
  openai: {
    ocr: 'gpt-4o',
    llm: 'gpt-3.5-turbo',
    tts: 'tts-1',
  },
  baidu: {
    ocr: 'general_basic',
    llm: '',
    tts: '',
  },
  tencent: {
    ocr: '',
    llm: '',
    tts: 'default',
  },
};

// 每个提供商的默认base_url
const defaultBaseUrls: Record<string, string> = {
  xiaomi: 'https://api.xiaomi.com/v1',
  'xiaomi-tokenplan': 'https://token-plan-cn.xiaomimimo.com/v1',
  openai: 'https://api.openai.com/v1',
  baidu: 'https://aip.baidubce.com',
  tencent: 'https://tts.tencentcloudapi.com',
};

const Profile: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const [selectedProvider, setSelectedProvider] = useState<string>('xiaomi-tokenplan');

  useEffect(() => {
    fetchApiKeys();
    // 设置默认值
    const serviceType = 'llm'; // 默认服务类型
    form.setFieldsValue({
      provider: 'xiaomi-tokenplan',
      service_type: serviceType,
      base_url: defaultBaseUrls['xiaomi-tokenplan'],
      model_name: defaultModels['xiaomi-tokenplan'][serviceType],
    });
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
      setSelectedProvider('');
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

  // 当提供商改变时，自动填充默认值
  const handleProviderChange = (value: string) => {
    setSelectedProvider(value);
    const serviceType = form.getFieldValue('service_type') || 'llm';
    form.setFieldsValue({
      base_url: defaultBaseUrls[value] || '',
      model_name: defaultModels[value]?.[serviceType] || '',
    });
  };

  // 当服务类型改变时，更新模型名称
  const handleServiceTypeChange = (value: string) => {
    const provider = form.getFieldValue('provider');
    if (provider && defaultModels[provider]) {
      form.setFieldsValue({
        model_name: defaultModels[provider][value] || '',
      });
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
            <Select placeholder="选择服务类型" onChange={handleServiceTypeChange}>
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
            <Select placeholder="选择服务提供商" onChange={handleProviderChange}>
              <Option value="xiaomi-tokenplan">小米 (Token Plan)</Option>
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
          <Form.Item
            name="base_url"
            label="API端点 (Base URL)"
            tooltip="自定义API端点地址，留空使用默认值"
          >
            <Input
              prefix={<LinkOutlined />}
              placeholder={selectedProvider ? defaultBaseUrls[selectedProvider] : '自定义API端点'}
            />
          </Form.Item>
          <Form.Item
            name="model_name"
            label="模型名称"
            tooltip="自定义模型名称，留空使用默认值"
          >
            <Input
              prefix={<RobotOutlined />}
              placeholder={selectedProvider ? (defaultModels[selectedProvider]?.[form.getFieldValue('service_type')] || '自定义模型名称') : '自定义模型名称'}
            />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认" valuePropName="checked">
            <Switch />
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
              <Space direction="vertical" size={4} style={{ flex: 1 }}>
                <Space>
                  <Tag color={item.is_default ? 'green' : 'default'}>
                    {item.service_type.toUpperCase()}
                  </Tag>
                  <span>{item.provider}</span>
                  {item.is_default && (
                    <Tag color="blue">默认</Tag>
                  )}
                </Space>
                {item.base_url && (
                  <div style={{ color: '#666', fontSize: 12 }}>
                    <LinkOutlined /> {item.base_url}
                  </div>
                )}
                {item.model_name && (
                  <div style={{ color: '#666', fontSize: 12 }}>
                    <RobotOutlined /> {item.model_name}
                  </div>
                )}
              </Space>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Profile;

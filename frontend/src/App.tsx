import { useState } from 'react'
import { Button, Space, Typography } from 'antd'
import { AudioOutlined } from '@ant-design/icons'

const { Title, Paragraph } = Typography

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <Title level={1}>语音转换助手</Title>
      <Paragraph>基于 AI 的语音转换工具</Paragraph>
      <Space>
        <Button
          type="primary"
          icon={<AudioOutlined />}
          onClick={() => setCount((count) => count + 1)}
        >
          点击测试 ({count})
        </Button>
      </Space>
    </div>
  )
}

export default App

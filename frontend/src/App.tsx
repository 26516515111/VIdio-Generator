import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import { AudioOutlined } from '@ant-design/icons'
import Login from './pages/Login'
import Register from './pages/Register'
import UserAuth from './components/UserAuth'

const { Header, Content, Footer } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>
          <AudioOutlined style={{ marginRight: 8 }} />
          语音转换助手
        </div>
        <UserAuth />
      </Header>
      <Content style={{ padding: '24px 48px' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        语音转换助手 ©2026 Created with FastAPI + React
      </Footer>
    </Layout>
  )
}

function HomePage() {
  return (
    <div style={{ textAlign: 'center', padding: '40px' }}>
      <h1>欢迎使用语音转换助手</h1>
      <p>基于 AI 的语音转换工具</p>
    </div>
  )
}

export default App

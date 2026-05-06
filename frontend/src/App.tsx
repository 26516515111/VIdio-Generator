import React from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Layout, Menu } from 'antd';
import { HomeOutlined, UserOutlined, LoginOutlined, AudioOutlined } from '@ant-design/icons';
import type { RootState } from './store';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import UserAuth from './components/UserAuth';

const { Header, Content, Footer } = Layout;

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useSelector((state: RootState) => state.auth);
  return token ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const { token } = useSelector((state: RootState) => state.auth);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: '首页',
    },
    ...(token
      ? [
          {
            key: 'profile',
            icon: <UserOutlined />,
            label: '个人中心',
          },
        ]
      : [
          {
            key: 'login',
            icon: <LoginOutlined />,
            label: '登录',
          },
        ]),
  ];

  const handleMenuClick = (info: { key: string }) => {
    switch (info.key) {
      case 'home':
        navigate('/');
        break;
      case 'profile':
        navigate('/profile');
        break;
      case 'login':
        navigate('/login');
        break;
    }
  };

  const selectedKey = location.pathname === '/' ? 'home' : location.pathname.slice(1);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold', marginRight: 40 }}>
          <AudioOutlined style={{ marginRight: 8 }} />
          语音转换助手
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          items={menuItems}
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
          style={{ flex: 1 }}
        />
        <UserAuth />
      </Header>
      <Content style={{ padding: '0 50px' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            }
          />
        </Routes>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        语音转换助手 ©2026 Created with FastAPI + React
      </Footer>
    </Layout>
  );
};

export default App;

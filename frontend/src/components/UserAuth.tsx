import React, { useEffect } from 'react';
import { Button, Space, Avatar, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { UserOutlined, LogoutOutlined, ProfileOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { logout, fetchCurrentUser } from '../store/authSlice';

const UserAuth: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user, token } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (token && !user) {
      dispatch(fetchCurrentUser());
    }
  }, [token, user, dispatch]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  if (!token) {
    return (
      <Space>
        <Button type="link" onClick={() => navigate('/login')}>
          登录
        </Button>
        <Button type="link" onClick={() => navigate('/register')}>
          注册
        </Button>
      </Space>
    );
  }

  const items: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <ProfileOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Dropdown menu={{ items }} placement="bottomRight">
      <Space style={{ cursor: 'pointer' }}>
        <Avatar icon={<UserOutlined />} />
        <span>{user?.username || '用户'}</span>
      </Space>
    </Dropdown>
  );
};

export default UserAuth;

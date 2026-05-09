import React from 'react';
import { Button, Avatar, Dropdown, Space } from 'antd';
import type { MenuProps } from 'antd';
import {
  AudioOutlined,
  UserOutlined,
  LogoutOutlined,
  ProfileOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { logout } from '../store/authSlice';
import styles from './ChatHeader.module.css';

const ChatHeader: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user, token } = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <ProfileOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <header className={styles.header}>
      <div className={styles.logo} onClick={() => navigate('/')}>
        <AudioOutlined className={styles.logoIcon} />
        <span className={styles.logoText}>语音转换助手</span>
      </div>

      <div className={styles.center} />

      <div className={styles.right}>
        {token ? (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space className={styles.userDropdown}>
              <Avatar size="small" icon={<UserOutlined />} />
              <span className={styles.username}>{user?.username || '用户'}</span>
            </Space>
          </Dropdown>
        ) : (
          <div className={styles.authButtons}>
            <Button type="link" size="small" onClick={() => navigate('/login')}>
              登录
            </Button>
            <Button type="link" size="small" onClick={() => navigate('/register')}>
              注册
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};

export default ChatHeader;

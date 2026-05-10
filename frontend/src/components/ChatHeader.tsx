import React from 'react';
import { Dropdown, Space } from 'antd';
import type { MenuProps } from 'antd';
import {
  AudioOutlined,
  LogoutOutlined,
  ProfileOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { logout } from '../store/authSlice';
import { setDrawerOpen } from '../store/settingsSlice';
import styles from './ChatHeader.module.css';

const ChatHeader: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { user, token } = useSelector((state: RootState) => state.auth);
  const settings = useSelector((state: RootState) => state.settings);

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
      onClick: () => dispatch(setDrawerOpen(true)),
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

  // Get display model name
  const getModelDisplay = () => {
    if (!settings.selectedModel) return null;
    const parts = settings.selectedModel.split(':');
    if (parts.length >= 3) return parts[2];
    if (parts.length >= 2) return parts[1];
    return parts[0];
  };

  const modelName = getModelDisplay();

  return (
    <header className={styles.header}>
      <div className={styles.logo} onClick={() => navigate('/')}>
        <div className={styles.logoIcon}>
          <AudioOutlined />
        </div>
        <span className={styles.logoText}>语音转换助手</span>
      </div>

      <div className={styles.center}>
        {modelName && (
          <div className={styles.modelBadge}>
            <span className={styles.modelDot} />
            {modelName}
          </div>
        )}
      </div>

      <div className={styles.right}>
        {token ? (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space className={styles.userDropdown}>
              <div className={styles.userAvatar}>
                {(user?.username || 'U')[0].toUpperCase()}
              </div>
              <span className={styles.username}>{user?.username || '用户'}</span>
            </Space>
          </Dropdown>
        ) : (
          <div className={styles.authButtons}>
            <button className={styles.loginBtn} onClick={() => navigate('/login')}>
              登录
            </button>
            <button className={styles.registerBtn} onClick={() => navigate('/register')}>
              注册
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default ChatHeader;

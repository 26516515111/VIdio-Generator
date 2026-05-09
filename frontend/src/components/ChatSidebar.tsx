import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { PlusOutlined, MenuOutlined, CloseOutlined } from '@ant-design/icons';
import type { RootState } from '../store';
import { clearChat } from '../store/chatSlice';
import styles from './ChatSidebar.module.css';

const ChatSidebar: React.FC = () => {
  const dispatch = useDispatch();
  const { messages } = useSelector((state: RootState) => state.chat);
  const [collapsed, setCollapsed] = useState(false);

  const handleNewChat = () => {
    dispatch(clearChat());
  };

  // Group messages into conversation entries (user messages as titles)
  const conversationItems = messages
    .filter((msg) => msg.role === 'user')
    .map((msg) => ({
      id: msg.id,
      text: msg.content.slice(0, 30) + (msg.content.length > 30 ? '...' : ''),
      time: new Date(msg.timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    }));

  return (
    <>
      {/* Mobile toggle button (visible when sidebar is collapsed) */}
      {collapsed && (
        <button
          className={styles.mobileToggle}
          onClick={() => setCollapsed(false)}
        >
          <MenuOutlined />
        </button>
      )}

      <aside
        className={`${styles.sidebar} ${collapsed ? styles.sidebarCollapsed : ''}`}
      >
        <div className={styles.header}>
          <button className={styles.newChatBtn} onClick={handleNewChat}>
            <PlusOutlined /> 新对话
          </button>
          <button
            className={styles.toggleBtn}
            onClick={() => setCollapsed(true)}
          >
            <CloseOutlined />
          </button>
        </div>

        <div className={styles.list}>
          {conversationItems.length === 0 ? (
            <div className={styles.empty}>暂无对话记录</div>
          ) : (
            conversationItems.map((item) => (
              <div key={item.id} className={styles.item}>
                <div className={styles.itemText}>{item.text}</div>
                <div className={styles.itemTime}>{item.time}</div>
              </div>
            ))
          )}
        </div>
      </aside>
    </>
  );
};

export default ChatSidebar;

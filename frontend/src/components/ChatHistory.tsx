import React, { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import ChatMessage from './ChatMessage';
import EmptyState from './EmptyState';
import styles from './ChatHistory.module.css';

interface ChatHistoryProps {
  onCapabilityClick?: (key: string) => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ onCapabilityClick }) => {
  const { messages } = useSelector((state: RootState) => state.chat);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return <EmptyState onCapabilityClick={onCapabilityClick} />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.messages}>
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={scrollAnchorRef} className={styles.scrollAnchor} />
      </div>
    </div>
  );
};

export default ChatHistory;

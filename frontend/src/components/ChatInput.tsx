import React, { useRef, useEffect } from 'react';
import { Button, Tag } from 'antd';
import {
  SendOutlined,
  ThunderboltOutlined,
  PictureOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  onSend: (text: string) => void;
  onPolish?: (text: string) => Promise<string | null>;
  onImageUpload?: () => void;
  onSettingsClick?: () => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onPolish,
  onImageUpload,
  onSettingsClick,
  disabled = false,
}) => {
  const settings = useSelector((state: RootState) => state.settings);
  const [text, setText] = React.useState('');
  const [mode, setMode] = React.useState<'text' | 'image'>('text');
  const [polishedText, setPolishedText] = React.useState<string | null>(null);
  const [isPolishing, setIsPolishing] = React.useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    setPolishedText(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handlePolish = async () => {
    if (!onPolish || !text.trim() || isPolishing) return;
    setIsPolishing(true);
    try {
      const result = await onPolish(text);
      if (result) {
        setPolishedText(result);
      }
    } finally {
      setIsPolishing(false);
    }
  };

  const handleUsePolished = () => {
    if (polishedText) {
      setText(polishedText);
      setPolishedText(null);
    }
  };

  const handleCancelPolished = () => {
    setPolishedText(null);
  };

  // Settings summary labels
  const voiceLabels: Record<string, string> = {
    mimo_default: '默认音色',
    default_zh: '中文女声',
    default_en: '英文女声',
    custom: '自定义音色',
  };
  const emotionLabels: Record<string, string> = {
    '开心': '开心', '悲伤': '悲伤', '愤怒': '愤怒', '惊讶': '惊讶',
    '恐惧': '恐惧', '厌恶': '厌恶', '平静': '平静', '激动': '激动', '温柔': '温柔',
  };

  const settingsSummary: string[] = [];
  if (settings.selectedVoice && settings.selectedVoice !== 'mimo_default') {
    settingsSummary.push(`音色: ${voiceLabels[settings.selectedVoice] || settings.selectedVoice}`);
  }
  if (settings.selectedEmotion && settings.selectedEmotion !== 'neutral') {
    settingsSummary.push(`情绪: ${emotionLabels[settings.selectedEmotion] || settings.selectedEmotion}`);
  }
  if (settings.directorMode) {
    settingsSummary.push('导演模式');
  }

  return (
    <div className={styles.container}>
      <div className={styles.inner}>
        {/* Polished text preview */}
        {polishedText && (
          <div className={styles.polishPreview}>
            <div className={styles.polishLabel}>AI润色结果：</div>
            <div className={styles.polishText}>{polishedText}</div>
            <div className={styles.polishActions}>
              <Button size="small" type="primary" onClick={handleUsePolished}>
                使用
              </Button>
              <Button size="small" onClick={handleCancelPolished}>
                取消
              </Button>
            </div>
          </div>
        )}

        {/* Settings summary tags */}
        {settingsSummary.length > 0 && (
          <div className={styles.settingsSummary}>
            {settingsSummary.map((tag) => (
              <Tag key={tag} color="blue" className={styles.settingsTag}>
                {tag}
              </Tag>
            ))}
          </div>
        )}

        <div className={styles.inputRow}>
          <textarea
            ref={textareaRef}
            className={styles.textarea}
            placeholder={disabled ? '处理中...' : '输入要转换的文字...'}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
          />
          <Button
            className={styles.sendBtn}
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            disabled={disabled || !text.trim()}
          />
        </div>

        <div className={styles.actions}>
          <button
            className={styles.actionBtn}
            onClick={handlePolish}
            disabled={disabled || isPolishing || !text.trim()}
          >
            <ThunderboltOutlined /> {isPolishing ? '润色中...' : 'AI润色'}
          </button>
          <button className={styles.actionBtn} onClick={onImageUpload} disabled={disabled}>
            <PictureOutlined /> 图片上传
          </button>

          <div className={styles.modeToggle}>
            <button
              className={`${styles.modeBtn} ${mode === 'text' ? styles.modeBtnActive : ''}`}
              onClick={() => setMode('text')}
            >
              文字
            </button>
            <button
              className={`${styles.modeBtn} ${mode === 'image' ? styles.modeBtnActive : ''}`}
              onClick={() => setMode('image')}
            >
              图片
            </button>
          </div>

          <button className={styles.settingsBtn} onClick={onSettingsClick}>
            <SettingOutlined />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;

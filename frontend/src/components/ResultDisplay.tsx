import React, { useRef, useState } from 'react';
import { Button, Card, Divider, message, Space, Typography } from 'antd';
import {
  DownloadOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import { ttsApi } from '../services/ttsApi';

const { Paragraph, Text } = Typography;

interface ResultDisplayProps {
  processedText: string;
  emotion: string;
  audioUrl?: string;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({
  processedText,
  emotion,
  audioUrl,
}) => {
  const [loading, setLoading] = useState(false);
  const [generatedAudioUrl, setGeneratedAudioUrl] = useState<string | null>(
    audioUrl || null
  );
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleGenerateAudio = async () => {
    if (!processedText.trim()) {
      message.error('没有可转换的文字');
      return;
    }

    setLoading(true);
    try {
      const result = await ttsApi.synthesize(processedText, 'default', emotion);
      setGeneratedAudioUrl(result.audio_url);
      message.success('语音生成成功');
    } catch (error) {
      message.error('语音生成失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleDownload = () => {
    if (generatedAudioUrl) {
      const link = document.createElement('a');
      link.href = generatedAudioUrl;
      link.download = 'speech.mp3';
      link.click();
    }
  };

  return (
    <Card title="处理结果">
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>处理后的文字：</Text>
          <Paragraph
            style={{
              padding: 16,
              background: '#f5f5f5',
              borderRadius: 8,
              marginTop: 8,
            }}
          >
            {processedText || '等待处理...'}
          </Paragraph>
        </div>

        <div>
          <Text strong>检测到的情绪：</Text>
          <Text style={{ marginLeft: 8 }}>{emotion || '未知'}</Text>
        </div>

        <Divider />

        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleGenerateAudio}
            loading={loading}
            disabled={!processedText}
          >
            生成语音
          </Button>

          {generatedAudioUrl && (
            <>
              <Button
                icon={
                  isPlaying ? (
                    <PauseCircleOutlined />
                  ) : (
                    <PlayCircleOutlined />
                  )
                }
                onClick={handlePlayPause}
              >
                {isPlaying ? '暂停' : '播放'}
              </Button>
              <Button icon={<DownloadOutlined />} onClick={handleDownload}>
                下载
              </Button>
            </>
          )}
        </Space>

        {generatedAudioUrl && (
          <audio
            ref={audioRef}
            src={generatedAudioUrl}
            onEnded={() => setIsPlaying(false)}
            style={{ display: 'none' }}
          />
        )}
      </Space>
    </Card>
  );
};

export default ResultDisplay;

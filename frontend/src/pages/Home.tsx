import React from 'react';
import { Row, Col, Space } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState, AppDispatch } from '../store';
import { setText, setScene } from '../store/inputSlice';
import { setProcessedText, setDetectedEmotion, setAudioUrl } from '../store/resultSlice';
import InputSection from '../components/InputSection';
import SceneInterpretation from '../components/SceneInterpretation';
import ResultDisplay from '../components/ResultDisplay';

const Home: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { text, scene } = useSelector((state: RootState) => state.input);
  const { processedText, detectedEmotion, audioUrl } = useSelector(
    (state: RootState) => state.result
  );

  const handleTextExtracted = (extractedText: string, detectedScene: string) => {
    dispatch(setText(extractedText));
    dispatch(setScene(detectedScene));
  };

  const handleProcessed = (newProcessedText: string, newEmotion: string) => {
    dispatch(setProcessedText(newProcessedText));
    dispatch(setDetectedEmotion(newEmotion));
    dispatch(setAudioUrl(null)); // 重置音频URL
  };

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={[24, 24]}>
        <Col span={12}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <InputSection onTextExtracted={handleTextExtracted} />
            <SceneInterpretation
              text={text}
              scene={scene}
              onProcessed={handleProcessed}
            />
          </Space>
        </Col>
        <Col span={12}>
          <ResultDisplay
            processedText={processedText}
            emotion={detectedEmotion}
            audioUrl={audioUrl || undefined}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Home;

import React, { useState, useCallback } from 'react';
import { message } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState, AppDispatch } from '../store';
import { addMessage, updateMessage, setProcessing } from '../store/chatSlice';
import type { ChatMessage } from '../types/chat';
import ChatSidebar from '../components/ChatSidebar';
import ChatHeader from '../components/ChatHeader';
import ChatHistory from '../components/ChatHistory';
import ChatInput from '../components/ChatInput';
import SettingsDrawer from '../components/SettingsDrawer';
import { llmApi } from '../services/llmApi';
import { ttsApi } from '../services/ttsApi';

const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

const Home: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { isProcessing } = useSelector((state: RootState) => state.chat);
  const settings = useSelector((state: RootState) => state.settings);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSend = useCallback(async (text: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
      originalText: text,
    };
    dispatch(addMessage(userMessage));

    // Add assistant placeholder
    const assistantId = generateId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      isProcessing: true,
    };
    dispatch(addMessage(assistantMessage));
    dispatch(setProcessing(true));

    // Parse selectedModel (format: "service_type:provider:model_name")
    const modelParts = settings.selectedModel.split(':');
    const provider = modelParts.length >= 2 ? modelParts[1] : 'xiaomi-tokenplan';

    try {
      // Director mode: skip LLM, send text directly to TTS with director instructions
      // Normal mode: send text directly to TTS (no LLM processing unless AI polish is used)
      let processedText = text;
      
      // Note: AI polish is handled separately by handlePolish function
      // Here we just send the text directly to TTS

      // Generate audio - convert scene to style description using LLM (only if scene exists)
      let styleDescription = settings.scene;
      
      if (!settings.directorMode && settings.scene) {
        try {
          const styleResult = await llmApi.sceneToStyle(settings.scene, provider);
          styleDescription = styleResult.style_description;
        } catch (error) {
          console.error('Failed to convert scene to style:', error);
          styleDescription = settings.scene;
        }
      }

      // TTS call
      // Determine custom voice parameters
      let customVoiceType: string | undefined;
      let customVoiceData: string | undefined;

      if (settings.selectedVoice === 'custom') {
        if (settings.customVoiceFile) {
          // Voice clone mode
          customVoiceType = 'voiceclone';
          // Convert file to base64
          const fileReader = new FileReader();
          const base64 = await new Promise<string>((resolve) => {
            fileReader.onload = () => {
              const result = fileReader.result as string;
              resolve(result.split(',')[1]); // Remove data:audio/mpeg;base64, prefix
            };
            fileReader.readAsDataURL(settings.customVoiceFile!);
          });
          customVoiceData = base64;
        } else if (settings.customVoiceName) {
          // Voice design mode
          customVoiceType = 'voicedesign';
          customVoiceData = settings.customVoiceName; // Text description
        }
      }

      const audioResult = await ttsApi.synthesize(
        processedText,
        settings.selectedVoice,
        settings.directorMode ? undefined : settings.selectedEmotion,
        undefined,  // No style tags
        settings.directorMode ? undefined : styleDescription,
        settings.directorMode ? settings.character : undefined,
        settings.directorMode ? settings.direction : undefined,
        customVoiceType,
        customVoiceData,
        provider
      );

      // Update assistant message
      dispatch(updateMessage({
        id: assistantId,
        updates: {
          content: processedText,
          processedText: processedText,
          detectedEmotion: 'neutral',
          audioUrl: audioResult.audio_url,
          isProcessing: false,
        },
      }));

      message.success('处理完成');
    } catch (error) {
      dispatch(updateMessage({
        id: assistantId,
        updates: {
          content: '处理失败，请重试',
          isProcessing: false,
        },
      }));
      message.error('处理失败');
    } finally {
      dispatch(setProcessing(false));
    }
  }, [dispatch, settings]);

  const handlePolish = useCallback(async (text: string): Promise<string | null> => {
    // Parse selectedModel (format: "service_type:provider:model_name")
    const modelParts = settings.selectedModel.split(':');
    const provider = modelParts.length >= 2 ? modelParts[1] : 'xiaomi-tokenplan';

    try {
      const result = await llmApi.polishText(text, settings.scene, provider);
      message.success('润色完成');
      return result.processed_text;
    } catch (error) {
      message.error('润色失败');
      return null;
    }
  }, [settings.scene, settings.selectedModel]);

  const handleImageUpload = useCallback(async () => {
    // TODO: Implement image upload with OCR
    message.info('图片上传功能开发中');
  }, []);

  const handleCapabilityClick = useCallback((capability: string) => {
    switch (capability) {
      case 'image':
        handleImageUpload();
        break;
      case 'director':
        setSettingsOpen(true);
        break;
      default:
        break;
    }
  }, [handleImageUpload]);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <ChatSidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatHeader />
        <ChatHistory onCapabilityClick={handleCapabilityClick} />
        <ChatInput
          onSend={handleSend}
          onPolish={handlePolish}
          onImageUpload={handleImageUpload}
          onSettingsClick={() => setSettingsOpen(true)}
          disabled={isProcessing}
        />
      </div>
      <SettingsDrawer
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  );
};

export default Home;

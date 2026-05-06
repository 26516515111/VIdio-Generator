# 语音转换助手

一个智能语音转换工具，支持文字输入和图片OCR，通过大模型加工后生成语音。

## 功能特性

- 📝 **文字输入**：直接输入要转换的文字
- 🖼️ **图片OCR**：上传图片自动提取文字
- 🎭 **场景演绎**：根据场景自动推断情绪
- 🤖 **大模型加工**：智能润色、情绪增强、风格转换
- 🔊 **语音合成**：多种音色、情绪控制
- 👤 **用户系统**：注册登录、历史记录、API密钥管理

## 快速开始

### 方式一：直接运行（推荐）

1. 下载 `语音转换助手.exe`
2. 双击运行
3. 打开浏览器访问 `http://localhost:8000`

### 方式二：从源码构建

#### 前提条件

- Node.js 18+
- Python 3.11+
- Git

#### 构建步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/voice-converter.git
cd voice-converter

# 构建
python backend/build.py
```

#### 运行

```bash
# 运行可执行文件
./backend/dist/语音转换助手.exe
```

## 配置

### API密钥配置

首次运行需要配置API密钥：

1. 访问 `http://localhost:8000`
2. 注册账号并登录
3. 进入"个人中心"
4. 添加API密钥（默认使用小米服务）

### 支持的服务提供商

| 服务类型 | 小米（默认） | OpenAI | 百度 | 腾讯 |
|---------|-------------|--------|------|------|
| OCR | ✅ | - | ✅ | ✅ |
| 大语言模型 | ✅ | ✅ | - | - |
| TTS | ✅ | - | - | ✅ |

## 开发

### 项目结构

```
语音转换助手/
├── frontend/          # 前端代码（React + TypeScript）
├── backend/           # 后端代码（Python + FastAPI）
├── docs/              # 文档
└── tests/             # 测试
```

### 开发模式

```bash
# 启动后端
cd backend
python run.py

# 启动前端（新终端）
cd frontend
npm run dev
```

访问 `http://localhost:3000` 进行开发。

### 运行测试

```bash
# 前端测试
cd frontend
npm test

# 后端测试
cd backend
pytest
```

## 技术栈

- **前端**：React 18, TypeScript, Redux Toolkit, Ant Design, Vite
- **后端**：Python 3.11, FastAPI, SQLAlchemy, SQLite
- **打包**：PyInstaller

## 许可证

MIT License

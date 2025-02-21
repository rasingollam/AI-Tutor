# 📱 AI Math Tutor

An intelligent mobile application that helps students learn mathematics through interactive, step-by-step problem solving with AI-powered guidance.

![AI Math Tutor Banner](mobile/assets/banner.png)

## ✨ Features

- 📸 **Image-based Problem Input**: Take a photo of your math problem or upload from gallery
- 🤖 **AI-powered Problem Analysis**: Instant problem recognition and understanding
- 🎯 **Step-by-Step Guidance**: Break down complex problems into manageable steps
- 💡 **Smart Hints**: Get contextual hints when stuck
- ✅ **Real-time Validation**: Immediate feedback on your answers
- 📊 **Progress Tracking**: Monitor your learning journey
- 🎨 **Modern UI/UX**: Clean, intuitive interface designed for learning

## 🛠️ Technology Stack

### Mobile App (React Native)
- React Native with Expo
- React Navigation for routing
- Axios for API communication
- Expo Image Picker for camera/gallery access
- Modern UI components with custom styling

### Backend (FastAPI)
- FastAPI for high-performance API
- Groq for AI processing
- Python Pillow for image handling
- Custom AI modules for:
  - Problem Understanding
  - Knowledge Assessment
  - Scaffolding Generation
  - Feedback Engine
  - Knowledge Reinforcement

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.9+
- Expo CLI
- Groq API key

### Backend Setup
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your Groq API key
./run_dev.sh  # On Windows: run_dev.bat
```

### Mobile App Setup
```bash
cd mobile
npm install
npx expo start
```

## 📱 App Structure

### Mobile App
```
mobile/
├── src/
│   ├── screens/         # Main app screens
│   │   ├── HomeScreen   # Problem input & history
│   │   └── TutorScreen  # Interactive problem solving
│   └── services/        # API integration
├── assets/             # Images and static files
└── App.js             # App entry point
```

### Backend
```
api/
├── modules/
│   ├── problem_understanding/  # Problem analysis
│   ├── scaffolding/           # Step generation
│   ├── feedback/              # Answer validation
│   └── knowledge_assessment/  # Learning progress
└── main.py                    # API endpoints
```

## 🎯 Key Features Explained

### 1. Problem Recognition
- Upload math problems through camera or gallery
- AI-powered text recognition and problem parsing
- Support for various math problem types

### 2. Interactive Learning
- Dynamic step generation based on problem complexity
- Contextual hints for each step
- Real-time answer validation
- Clear explanations for correct and incorrect answers

### 3. User Experience
- Clean, intuitive interface
- Progress indicators
- Easy navigation between steps
- Visual feedback for actions

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for AI processing
- [Expo](https://expo.dev/) for React Native tooling
- [FastAPI](https://fastapi.tiangolo.com/) for backend framework

---
Built with ❤️ by Jivita.

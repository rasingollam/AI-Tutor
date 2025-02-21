import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  Image,
  SafeAreaView,
  Modal,
} from 'react-native';
import { validateAnswer } from '../services/api';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';

export default function TutorScreen({ route, navigation }) {
  const { steps = [], problem = '' } = route.params || {};
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [userAnswer, setUserAnswer] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [feedback, setFeedback] = useState({ message: '', isError: false });
  const [problemCompleted, setProblemCompleted] = useState(false);
  const [selectedStep, setSelectedStep] = useState(null);
  const maxAttempts = 5;

  // Ensure we have valid steps data
  useEffect(() => {
    if (!Array.isArray(steps) || steps.length === 0) {
      console.error('Invalid steps data:', steps);
      Alert.alert(
        'Error',
        'No steps available for this problem',
        [{ text: 'Go Back', onPress: () => navigation.goBack() }]
      );
    } else {
      console.log('Valid steps data received:', steps);
    }
  }, [steps, navigation]);

  const pickImage = async () => {
    console.log('Starting image picker...');
    
    // Request permission
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    console.log('Image picker permission status:', status);
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant permission to access your photos.');
      return;
    }

    console.log('Launching image picker...');
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    console.log('Image picker result:', result);

    if (!result.canceled && result.assets && result.assets[0]) {
      console.log('Image selected:', result.assets[0].uri);
      setSelectedImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    console.log('Starting camera...');
    
    // Request camera permission
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    console.log('Camera permission status:', status);
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant permission to use the camera.');
      return;
    }

    console.log('Launching camera...');
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });

    console.log('Camera result:', result);

    if (!result.canceled && result.assets && result.assets[0]) {
      console.log('Photo taken:', result.assets[0].uri);
      setSelectedImage(result.assets[0].uri);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
  };

  // Get current step safely
  const currentStep = steps[currentStepIndex] || {};
  const isLastStep = currentStepIndex === steps.length - 1;

  const handleAnswerSubmit = async () => {
    if (!userAnswer.trim() && !selectedImage) {
      setFeedback({ message: 'Please enter an answer or select an image', isError: true });
      return;
    }

    if (!currentStep?.instruction || !currentStep?.expected_answer) {
      console.error('Invalid step data:', currentStep);
      setFeedback({ message: 'Invalid step data', isError: true });
      return;
    }

    setLoading(true);
    try {
      console.log('Validating answer for step:', currentStep);
      const validation = await validateAnswer(currentStep, userAnswer.trim(), selectedImage);
      console.log('Validation result:', validation);

      if (validation.success && validation.validation.is_correct) {
        // Add current step to completed steps with the user's answer
        const completedStep = {
          ...currentStep,
          userAnswer: userAnswer.trim(),
          userImage: selectedImage,
          explanation: validation.validation.explanation
        };
        setCompletedSteps([...completedSteps, completedStep]);
        setFeedback({ message: validation.validation.explanation, isError: false });
        
        setAttempts(0); // Reset attempts for next step
        
        if (!isLastStep) {
          setTimeout(() => {
            setCurrentStepIndex(prev => prev + 1);
            setUserAnswer('');
            setSelectedImage(null);
            setShowHint(false);
            setFeedback({ message: '', isError: false });
          }, 1500); // Give user time to see success feedback
        } else {
          setProblemCompleted(true);
          setFeedback({ message: '', isError: false }); // Clear feedback when problem is completed
        }
      } else {
        const newAttempts = attempts + 1;
        setAttempts(newAttempts);
        
        if (newAttempts >= maxAttempts) {
          // Add failed step to completed steps
          const completedStep = {
            ...currentStep,
            userAnswer: userAnswer.trim(),
            userImage: selectedImage,
            failed: true,
            explanation: validation.validation.explanation
          };
          setCompletedSteps([...completedSteps, completedStep]);
          
          setFeedback({ 
            message: `Maximum attempts reached. The correct answer was: ${currentStep.expected_answer}. ${currentStep.explanation}`, 
            isError: true 
          });

          if (!isLastStep) {
            setTimeout(() => {
              setCurrentStepIndex(prev => prev + 1);
              setUserAnswer('');
              setSelectedImage(null);
              setShowHint(false);
              setAttempts(0);
              setFeedback({ message: '', isError: false });
            }, 3000); // Give user more time to see the correct answer
          } else {
            navigation.goBack();
          }
        } else {
          setFeedback({ 
            message: `${validation.validation.explanation}\nAttempts remaining: ${maxAttempts - newAttempts}`, 
            isError: true 
          });
        }
      }
    } catch (error) {
      console.error('Error validating answer:', error);
      setFeedback({ message: 'Failed to validate answer. Please try again.', isError: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} bounces={false}>
        <View style={styles.problemCard}>
          <Text style={styles.problemLabel}>Problem:</Text>
          <Text style={styles.problemText}>{problem}</Text>
        </View>

        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${((currentStepIndex + 1) / steps.length) * 100}%` }]} />
        </View>

        {/* Completed Steps */}
        {completedSteps.map((step, index) => (
          <View key={index} style={styles.completedStepContainer}>
            <View style={styles.stepHeader}>
              <Text style={styles.stepNumber}>Step {index + 1}</Text>
              {!step.failed && (
                <TouchableOpacity 
                  onPress={() => setSelectedStep(step)}
                  style={styles.explanationIcon}
                >
                  <Ionicons name="information-circle-outline" size={24} color="#007AFF" />
                </TouchableOpacity>
              )}
            </View>
            <Text style={styles.instruction}>{step.instruction}</Text>
            <View style={styles.answerRow}>
              <View style={styles.answerContainer}>
                <Text style={styles.answerLabel}>Your answer:</Text>
                <View style={[
                  styles.answerBox,
                  step.failed ? styles.failedAnswerBox : styles.correctAnswerBox
                ]}>
                  <Text style={[
                    styles.answer,
                    step.failed ? styles.failedAnswer : styles.correctAnswer
                  ]}>
                    {step.userAnswer}
                  </Text>
                </View>
              </View>
              {!step.failed && (
                <Ionicons name="checkmark-circle" size={24} color="#34C759" style={styles.checkmark} />
              )}
            </View>
          </View>
        ))}

        {/* Current Step */}
        <View style={styles.stepCard}>
          {!problemCompleted ? (
            <>
              <Text style={styles.stepCounter}>
                Step {currentStepIndex + 1} of {steps.length}
              </Text>
              <Text style={styles.instruction}>{currentStep.instruction}</Text>
            </>
          ) : (
            <View style={styles.completionContainer}>
              <Text style={styles.completionTitle}>Problem Solved! 🎉</Text>
              <Text style={styles.completionSubtitle}>
                Great job completing all the steps!
              </Text>
              <TouchableOpacity
                style={styles.tryAnotherButton}
                onPress={() => navigation.goBack()}
              >
                <Text style={styles.tryAnotherButtonText}>Try Another Problem</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Feedback Message */}
          {!problemCompleted && feedback.message ? (
            <Text style={[
              styles.feedbackText,
              feedback.isError ? styles.errorFeedback : styles.successFeedback
            ]}>
              {feedback.message}
            </Text>
          ) : null}

          {/* Answer Input Section - Only show if problem is not completed */}
          {!problemCompleted && (
            <>
              <View style={styles.answerContainer}>
                <TextInput
                  style={styles.answerInput}
                  value={userAnswer}
                  onChangeText={setUserAnswer}
                  placeholder="Enter your answer"
                  placeholderTextColor="#999"
                  multiline
                />
                
                <View style={styles.imageControls}>
                  <TouchableOpacity onPress={takePhoto} style={styles.imageButton}>
                    <Ionicons name="camera-outline" size={24} color="#007AFF" />
                  </TouchableOpacity>
                  <TouchableOpacity onPress={pickImage} style={styles.imageButton}>
                    <Ionicons name="image-outline" size={24} color="#007AFF" />
                  </TouchableOpacity>
                </View>

                {selectedImage && (
                  <View style={styles.imagePreviewContainer}>
                    <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
                    <TouchableOpacity style={styles.removeImageButton} onPress={removeImage}>
                      <Ionicons name="close-circle" size={24} color="#FF3B30" />
                    </TouchableOpacity>
                  </View>
                )}
              </View>

              <View style={styles.buttonContainer}>
                <TouchableOpacity
                  style={[styles.button, styles.hintButton]}
                  onPress={() => setShowHint(!showHint)}
                >
                  <Text style={styles.hintButtonText}>
                    {showHint ? 'Hide Hint' : 'Show Hint'}
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.button, styles.submitButton, loading && styles.submitButtonDisabled]}
                  onPress={handleAnswerSubmit}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#FFFFFF" />
                  ) : (
                    <Text style={styles.submitButtonText}>Submit Answer</Text>
                  )}
                </TouchableOpacity>
              </View>

              {showHint && (
                <View style={styles.hintContainer}>
                  <Text style={styles.hintText}>{currentStep.explanation}</Text>
                </View>
              )}

              <View style={styles.attemptsContainer}>
                <Text style={styles.attemptsText}>
                  Attempts remaining: {maxAttempts - attempts}
                </Text>
              </View>
            </>
          )}
        </View>
      </ScrollView>
      {/* Explanation Modal */}
      <Modal
        animationType="fade"
        transparent={true}
        visible={selectedStep !== null}
        onRequestClose={() => setSelectedStep(null)}
      >
        <TouchableOpacity 
          style={styles.modalOverlay}
          activeOpacity={1} 
          onPress={() => setSelectedStep(null)}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Explanation</Text>
              <TouchableOpacity onPress={() => setSelectedStep(null)}>
                <Ionicons name="close" size={24} color="#8E8E93" />
              </TouchableOpacity>
            </View>
            <Text style={styles.modalText}>
              {selectedStep?.explanation}
            </Text>
          </View>
        </TouchableOpacity>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F8F8',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  problemCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  problemLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  problemText: {
    fontSize: 16,
    color: '#3A3A3C',
    lineHeight: 24,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#E5E5EA',
    borderRadius: 2,
    marginBottom: 16,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
  },
  stepCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  stepHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  explanationIcon: {
    padding: 4,
  },
  stepCounter: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 8,
  },
  instruction: {
    fontSize: 16,
    color: '#1C1C1E',
    lineHeight: 24,
    marginBottom: 16,
  },
  answerContainer: {
    marginBottom: 16,
  },
  answerInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1C1C1E',
    minHeight: 100,
    textAlignVertical: 'top',
  },
  imageControls: {
    flexDirection: 'row',
    marginTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
    paddingTop: 8,
  },
  imageButton: {
    marginRight: 16,
    padding: 8,
  },
  imagePreviewContainer: {
    marginTop: 8,
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  imagePreview: {
    width: '100%',
    height: 200,
    resizeMode: 'contain',
    backgroundColor: '#F8F8F8',
  },
  removeImageButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 2,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  button: {
    flex: 1,
    borderRadius: 25,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hintButton: {
    backgroundColor: '#F2F2F7',
    marginRight: 8,
  },
  submitButton: {
    backgroundColor: '#007AFF',
    marginLeft: 8,
  },
  submitButtonDisabled: {
    opacity: 0.7,
  },
  hintButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  hintContainer: {
    backgroundColor: '#F2F2F7',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  hintText: {
    fontSize: 14,
    color: '#3A3A3C',
    lineHeight: 20,
  },
  attemptsContainer: {
    alignItems: 'center',
  },
  attemptsText: {
    fontSize: 14,
    color: '#8E8E93',
  },
  feedbackText: {
    marginVertical: 10,
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 8,
    fontSize: 16,
  },
  errorFeedback: {
    backgroundColor: '#FFE5E5',
    color: '#D32F2F',
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  successFeedback: {
    backgroundColor: '#E8F5E9',
    color: '#388E3C',
    borderWidth: 1,
    borderColor: '#C8E6C9',
  },
  completedStepContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  stepNumber: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 8,
  },
  answerRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  answerContainer: {
    flex: 1,
    marginRight: 8,
  },
  answerLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 4,
  },
  answerBox: {
    padding: 12,
    borderRadius: 8,
    marginTop: 4,
  },
  correctAnswerBox: {
    backgroundColor: '#E8F5E9',
    borderWidth: 1,
    borderColor: '#C8E6C9',
  },
  failedAnswerBox: {
    backgroundColor: '#FFEBEE',
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  answer: {
    fontSize: 16,
  },
  correctAnswer: {
    color: '#2E7D32',
    fontWeight: '600',
  },
  failedAnswer: {
    color: '#C62828',
  },
  checkmark: {
    marginLeft: 8,
    marginTop: 24,
  },
  completionContainer: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    marginVertical: 10,
  },
  completionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#388E3C',
    marginBottom: 10,
  },
  completionSubtitle: {
    fontSize: 16,
    color: '#4CAF50',
    textAlign: 'center',
    marginBottom: 20,
  },
  tryAnotherButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  tryAnotherButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    width: '100%',
    maxWidth: 500,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
  },
  modalText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
});

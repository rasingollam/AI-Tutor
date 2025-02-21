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
} from 'react-native';
import { validateAnswer } from '../services/api';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';

export default function TutorScreen({ route, navigation }) {
  const { steps = [], problem = '' } = route.params || {};
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [attempts, setAttempts] = useState(0);
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
      Alert.alert('Error', 'Please enter an answer or select an image');
      return;
    }

    if (!currentStep?.instruction || !currentStep?.expected_answer) {
      console.error('Invalid step data:', currentStep);
      Alert.alert('Error', 'Invalid step data');
      return;
    }

    setLoading(true);
    try {
      console.log('Validating answer for step:', currentStep);
      const validation = await validateAnswer(currentStep, userAnswer.trim(), selectedImage);
      console.log('Validation result:', validation);

      if (validation.success && validation.validation.is_correct) {
        setAttempts(0); // Reset attempts for next step
        Alert.alert(
          'Correct!',
          'Well done! Moving to next step...',
          [{ 
            text: 'Continue',
            onPress: () => {
              if (!isLastStep) {
                setCurrentStepIndex(prev => prev + 1);
                setUserAnswer('');
                setSelectedImage(null);
                setShowHint(false);
              } else {
                Alert.alert(
                  'Congratulations!',
                  'You have completed all steps!',
                  [{ text: 'Finish', onPress: () => navigation.goBack() }]
                );
              }
            }
          }]
        );
      } else {
        const newAttempts = attempts + 1;
        setAttempts(newAttempts);
        
        if (newAttempts >= maxAttempts) {
          Alert.alert(
            'Maximum Attempts Reached',
            `The correct answer was: ${currentStep.expected_answer}\n\nExplanation: ${currentStep.explanation}`,
            [{ 
              text: 'Next Step',
              onPress: () => {
                if (!isLastStep) {
                  setCurrentStepIndex(prev => prev + 1);
                  setUserAnswer('');
                  setSelectedImage(null);
                  setShowHint(false);
                  setAttempts(0);
                } else {
                  navigation.goBack();
                }
              }
            }]
          );
        } else {
          // Show specific error message if available
          const errorMessage = validation.error || 'Incorrect answer. Please try again.';
          Alert.alert(
            'Incorrect',
            `${errorMessage}\nYou have ${maxAttempts - newAttempts} attempts remaining.`
          );
        }
      }
    } catch (error) {
      console.error('Error validating answer:', error);
      Alert.alert('Error', 'Failed to validate answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!Array.isArray(steps) || steps.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>No steps available</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.problemContainer}>
        <Text style={styles.problemTitle}>Problem:</Text>
        <Text style={styles.problemText}>{problem}</Text>
      </View>

      <View style={styles.stepContainer}>
        <Text style={styles.stepTitle}>
          Step {currentStepIndex + 1} of {steps.length}
        </Text>
        <Text style={styles.instruction}>{currentStep.instruction}</Text>

        {showHint && (
          <View style={styles.hintContainer}>
            <Text style={styles.hintText}>{currentStep.explanation}</Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={userAnswer}
            onChangeText={setUserAnswer}
            placeholder="Enter your answer"
            placeholderTextColor="#999"
            multiline
          />
          <View style={styles.imageButtonsContainer}>
            <TouchableOpacity 
              style={styles.imageButton} 
              onPress={takePhoto}
            >
              <Ionicons name="camera-outline" size={24} color="#007AFF" />
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.imageButton} 
              onPress={pickImage}
            >
              <Ionicons name="image-outline" size={24} color="#007AFF" />
            </TouchableOpacity>
          </View>
        </View>

        {selectedImage && (
          <View style={styles.imagePreviewContainer}>
            <Image
              source={{ uri: selectedImage }}
              style={styles.imagePreview}
            />
            <TouchableOpacity 
              style={styles.removeImageButton}
              onPress={removeImage}
            >
              <Ionicons name="close-circle" size={24} color="#FF3B30" />
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.hintButton]}
            onPress={() => setShowHint(!showHint)}
          >
            <Text style={[styles.buttonText, { color: '#007AFF' }]}>
              {showHint ? 'Hide Hint' : 'Show Hint'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.submitButton]}
            onPress={handleAnswerSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.buttonText}>Submit</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F9F9',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 20,
  },
  problemContainer: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    margin: 20,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  problemTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  problemText: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  stepContainer: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    margin: 20,
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginBottom: 15,
  },
  instruction: {
    fontSize: 16,
    color: '#333',
    marginBottom: 20,
    lineHeight: 24,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
  },
  input: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: '#333',
    minHeight: 80,
  },
  imageButtonsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  imageButton: {
    padding: 12,
    alignSelf: 'flex-start',
  },
  imagePreviewContainer: {
    marginBottom: 20,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDD',
  },
  imagePreview: {
    width: '100%',
    height: 200,
    resizeMode: 'contain',
  },
  removeImageButton: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 4,
  },
  hintContainer: {
    backgroundColor: '#F0F9FF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
  },
  hintText: {
    fontSize: 14,
    color: '#0A84FF',
    lineHeight: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  hintButton: {
    backgroundColor: '#F2F2F7',
  },
  submitButton: {
    backgroundColor: '#007AFF',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

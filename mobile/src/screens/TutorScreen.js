import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform
} from 'react-native';
import { validateAnswer } from '../services/api';

export default function TutorScreen({ route, navigation }) {
  const { problem, steps } = route.params;
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [stepCompleted, setStepCompleted] = useState(false);

  const currentStep = steps[currentStepIndex];

  const handleAnswerSubmit = async () => {
    if (!userAnswer.trim()) {
      Alert.alert('Error', 'Please enter your answer');
      return;
    }

    setLoading(true);
    try {
      const response = await validateAnswer(currentStep, userAnswer);
      setLoading(false);

      if (response.success) {
        const { validation } = response;
        if (validation.is_correct) {
          setStepCompleted(true);
          Alert.alert(
            'Correct!', 
            validation.explanation,
            [
              { 
                text: 'Next Step', 
                onPress: handleNextStep 
              }
            ]
          );
        } else {
          setAttempts(prev => prev + 1);
          if (attempts >= 1) {
            Alert.alert(
              'Incorrect',
              `The correct answer was: ${currentStep.expected_answer}\n\nExplanation: ${currentStep.explanation}`,
              [
                { 
                  text: 'Next Step', 
                  onPress: handleNextStep 
                }
              ]
            );
          } else {
            Alert.alert('Incorrect', validation.explanation);
          }
        }
      } else {
        Alert.alert('Error', response.error || 'Failed to validate answer');
      }
    } catch (error) {
      setLoading(false);
      Alert.alert('Error', 'Failed to validate answer');
      console.error(error);
    }
  };

  const handleNextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
      setUserAnswer('');
      setShowHint(false);
      setAttempts(0);
      setStepCompleted(false);
    } else {
      Alert.alert(
        'Congratulations!',
        'You have completed all steps!',
        [
          {
            text: 'Start New Problem',
            onPress: () => navigation.navigate('Home')
          }
        ]
      );
    }
  };

  const toggleHint = () => {
    setShowHint(!showHint);
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.problemContainer}>
          <Text style={styles.label}>Problem:</Text>
          <Text style={styles.problemText}>{problem}</Text>
        </View>

        <View style={styles.stepContainer}>
          <Text style={styles.label}>Step {currentStepIndex + 1} of {steps.length}:</Text>
          <Text style={styles.instruction}>{currentStep.instruction}</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Enter your answer"
            value={userAnswer}
            onChangeText={setUserAnswer}
            multiline
            editable={!stepCompleted}
          />

          <TouchableOpacity 
            style={[styles.button, stepCompleted && styles.disabledButton]}
            onPress={handleAnswerSubmit}
            disabled={loading || stepCompleted}
          >
            <Text style={styles.buttonText}>Submit Answer</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.button, styles.hintButton]}
            onPress={toggleHint}
          >
            <Text style={styles.buttonText}>
              {showHint ? 'Hide Hint' : 'Show Hint'}
            </Text>
          </TouchableOpacity>

          {showHint && (
            <View style={styles.hintContainer}>
              <Text style={styles.hintText}>{currentStep.hint}</Text>
            </View>
          )}

          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.loadingText}>Checking answer...</Text>
            </View>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    padding: 20,
    flexGrow: 1,
  },
  problemContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#495057',
  },
  problemText: {
    fontSize: 18,
    color: '#212529',
  },
  stepContainer: {
    marginBottom: 20,
  },
  instruction: {
    fontSize: 16,
    marginBottom: 15,
    color: '#495057',
    lineHeight: 24,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    minHeight: 100,
    backgroundColor: '#f9f9f9',
    fontSize: 16,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
  },
  hintButton: {
    backgroundColor: '#5856D6',
  },
  hintContainer: {
    padding: 15,
    backgroundColor: '#e9ecef',
    borderRadius: 12,
    marginTop: 10,
  },
  hintText: {
    fontSize: 14,
    color: '#495057',
  },
  loadingContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
});

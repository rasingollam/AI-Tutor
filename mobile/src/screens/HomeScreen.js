import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { processProblem } from '../services/api';

export default function HomeScreen({ navigation }) {
  const [textProblem, setTextProblem] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTextSubmit = async () => {
    if (!textProblem.trim()) {
      Alert.alert('Error', 'Please enter a math problem');
      return;
    }

    setLoading(true);
    try {
      const response = await processProblem(textProblem);
      setLoading(false);
      
      if (response.success) {
        navigation.navigate('Tutor', {
          problem: textProblem,
          steps: response.steps.steps // Access the steps array from the response
        });
      } else {
        Alert.alert('Error', response.error || 'Failed to process problem');
      }
    } catch (error) {
      setLoading(false);
      Alert.alert('Error', 'Failed to process problem');
      console.error(error);
    }
  };

  const handleImagePick = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant camera roll permissions');
      return;
    }

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 1,
      });

      if (!result.canceled) {
        setLoading(true);
        const response = await processProblem(result.assets[0].uri, true);
        setLoading(false);
        
        if (response.success) {
          navigation.navigate('Tutor', {
            problem: response.problem,
            steps: response.steps.steps
          });
        } else {
          Alert.alert('Error', response.error || 'Failed to process image');
        }
      }
    } catch (error) {
      setLoading(false);
      Alert.alert('Error', 'Failed to process image');
      console.error(error);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>AI Math Tutor</Text>
        <Text style={styles.subtitle}>Enter a problem or upload an image</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Enter your math problem"
          value={textProblem}
          onChangeText={setTextProblem}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />

        <TouchableOpacity 
          style={styles.button}
          onPress={handleTextSubmit}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Solve Text Problem</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.imageButton]}
          onPress={handleImagePick}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Upload Image Problem</Text>
        </TouchableOpacity>

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Processing...</Text>
          </View>
        )}
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
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
    color: '#1a1a1a',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    borderRadius: 12,
    marginBottom: 20,
    minHeight: 120,
    backgroundColor: '#f9f9f9',
    fontSize: 16,
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
  imageButton: {
    backgroundColor: '#34C759',
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
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
});

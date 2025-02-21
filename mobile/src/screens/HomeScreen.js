import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Image,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { processProblem } from '../services/api';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen({ navigation }) {
  const [problemText, setProblemText] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant permission to access your photos.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant permission to use the camera.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
  };

  const handleSubmit = async () => {
    if (!problemText.trim() && !selectedImage) {
      Alert.alert('Error', 'Please enter a problem or select an image');
      return;
    }

    setLoading(true);
    try {
      const result = await processProblem(problemText.trim(), selectedImage);
      console.log('Problem processing response:', result);

      if (result.success && result.steps) {
        // Extract steps from the nested structure
        const steps = result.steps.steps || [];
        navigation.navigate('Tutor', {
          steps: steps,
          problem: result.problem || problemText || 'Image Problem'
        });
      } else {
        Alert.alert('Error', result.error || 'Failed to process problem');
      }
    } catch (error) {
      console.error('Error processing problem:', error);
      Alert.alert('Error', 'Failed to process problem. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.inputWrapper}>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={problemText}
            onChangeText={setProblemText}
            placeholder="Enter your math problem"
            placeholderTextColor="#999"
            multiline
          />
          <View style={styles.iconContainer}>
            <TouchableOpacity onPress={takePhoto}>
              <Ionicons name="camera-outline" size={24} color="#007AFF" />
            </TouchableOpacity>
            <TouchableOpacity onPress={pickImage} style={styles.galleryIcon}>
              <Ionicons name="image-outline" size={24} color="#007AFF" />
            </TouchableOpacity>
          </View>
        </View>

        {selectedImage && (
          <View style={styles.imagePreviewContainer}>
            <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
            <TouchableOpacity style={styles.removeButton} onPress={removeImage}>
              <Ionicons name="close-circle" size={24} color="#FF3B30" />
            </TouchableOpacity>
          </View>
        )}

        <TouchableOpacity
          style={[styles.solveButton, loading && styles.solveButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.solveButtonText}>Solve Problem</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '600',
  },
  inputWrapper: {
    padding: 16,
    flex: 1,
  },
  inputContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    marginBottom: 16,
  },
  input: {
    padding: 12,
    fontSize: 16,
    color: '#000000',
    minHeight: 100,
    textAlignVertical: 'top',
  },
  iconContainer: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
    padding: 8,
    justifyContent: 'flex-start',
  },
  galleryIcon: {
    marginLeft: 16,
  },
  imagePreviewContainer: {
    marginBottom: 16,
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
  removeButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 2,
  },
  solveButton: {
    backgroundColor: '#007AFF',
    borderRadius: 25,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  solveButtonDisabled: {
    opacity: 0.7,
  },
  solveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

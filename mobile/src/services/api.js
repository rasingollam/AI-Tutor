import axios from 'axios';

const API_BASE_URL = 'http://192.168.1.100:8000'; // Replace with your local IP address

export const processProblem = async (input, isImage = false) => {
  try {
    if (isImage) {
      // Create form data for image upload
      const formData = new FormData();
      formData.append('file', {
        uri: input,
        type: 'image/jpeg',
        name: 'problem.jpg',
      });

      const response = await axios.post(
        `${API_BASE_URL}/process-image-problem`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } else {
      // Process text problem
      const response = await axios.post(
        `${API_BASE_URL}/process-text-problem`,
        { problem: input }
      );
      return response.data;
    }
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to process problem'
    };
  }
};

export const validateAnswer = async (stepData, answer) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/validate-answer`,
      {
        step_data: stepData,
        answer: answer,
      }
    );
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to validate answer'
    };
  }
};

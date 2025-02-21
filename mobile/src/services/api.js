import axios from 'axios';

const API_BASE_URL = 'http://192.168.8.17:8000'; // Replace with your local IP address

console.log('API Base URL:', API_BASE_URL);

export const processProblem = async (text, imageUri = null) => {
  console.log('Processing problem:', { text, imageUri });
  
  try {
    const formData = new FormData();
    
    // Add text if provided
    if (text) {
      formData.append('text', text);
    }
    
    // Add image if provided
    if (imageUri) {
      console.log('Preparing image upload...');
      const uriParts = imageUri.split('.');
      const fileType = uriParts[uriParts.length - 1];
      
      formData.append('file', {
        uri: imageUri,
        type: `image/${fileType}`,
        name: `problem.${fileType}`,
      });
      console.log('Added image to FormData:', {
        uri: imageUri,
        type: `image/${fileType}`,
        name: `problem.${fileType}`
      });
    }

    console.log('Making POST request to /process-combined-problem');
    const response = await axios.post(
      `${API_BASE_URL}/process-combined-problem`,
      formData,
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
        transformRequest: (data, headers) => {
          return data; // Don't transform FormData
        },
      }
    );
    console.log('Problem processing response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error in processProblem:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers
    });
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to process problem'
    };
  }
};

export const validateAnswer = async (stepData, answer, imageUri = null) => {
  console.log('Validating answer:', { stepData, answer, imageUri });
  
  try {
    console.log('Making POST request to /validate-answer');
    const formData = new FormData();
    formData.append('step_data', JSON.stringify(stepData));
    
    // Ensure at least one of answer or image is provided
    if (!answer && !imageUri) {
      throw new Error('No answer provided');
    }
    
    if (answer) {
      formData.append('answer', answer);
    }
    
    if (imageUri) {
      console.log('Adding image to answer...');
      const uriParts = imageUri.split('.');
      const fileType = uriParts[uriParts.length - 1] || 'jpeg';
      
      formData.append('file', {
        uri: imageUri,
        type: `image/${fileType}`,
        name: `answer.${fileType}`,
      });
      console.log('Added image to FormData:', {
        uri: imageUri,
        type: `image/${fileType}`,
        name: `answer.${fileType}`
      });
    }

    const response = await axios.post(
      `${API_BASE_URL}/validate-answer`,
      formData,
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data'
        },
        transformRequest: (data, headers) => {
          return data;
        },
      }
    );
    console.log('Validation response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error in validateAnswer:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers
    });
    
    // Return a more user-friendly error
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to validate answer'
    };
  }
};

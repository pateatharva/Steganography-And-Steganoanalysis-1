import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Alert
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function Steganalysis() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setError('');
      setResult(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.bmp']
    },
    multiple: false
  });

  const handleAnalyze = async () => {
    if (!image) {
      setError('Please select an image to analyze');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('image', image);

      console.log('🔍 [STEGANALYSIS] Sending analysis request...');

      const response = await axios.post(
        'http://127.0.0.1:5000/steganalysis/analyze',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log('✅ [STEGANALYSIS] Backend response:', response.data);

      // Backend returns { is_stego: bool, confidence: float } directly
      if (response.data && response.data.is_stego !== undefined) {
        setResult(response.data);
        console.log('📊 [STEGANALYSIS] Analysis result:', response.data);
      } else {
        setError('Failed to get analysis results');
        console.warn('⚠️ [STEGANALYSIS] Invalid response format');
      }
    } catch (err) {
      console.error('❌ [STEGANALYSIS] Error:', err);
      setError(err.response?.data?.error || 'Failed to analyze image');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setError('');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Steganalysis - Detect Hidden Data
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper
            {...getRootProps()}
            sx={{
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.400',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              minHeight: 300
            }}
          >
            <input {...getInputProps()} />
            {preview ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Selected Image:
                </Typography>
                <img
                  src={preview}
                  alt="Upload"
                  style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }}
                />
              </Box>
            ) : (
              <Typography>
                {isDragActive ? 'Drop the image here...' : 'Drag and drop an image here, or click to select'}
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          {result ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Result:
                </Typography>
                <Typography variant="h5" color={result.is_stego ? 'error' : 'success'} gutterBottom>
                  {result.is_stego ? '🔍 Stego Image Detected' : '✅ Original Image (Clean)'}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Confidence: {(result.confidence * 100).toFixed(2)}%
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Analysis Details:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {result.is_stego 
                      ? 'This image appears to contain hidden data. It may have been modified using steganography techniques.'
                      : 'This image appears to be an original image without any hidden data embedded.'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Paper sx={{ p: 3, minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="text.secondary">
                Analysis results will appear here
              </Typography>
            </Paper>
          )}
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleAnalyze}
              disabled={loading || !image}
              size="large"
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Image'}
            </Button>
            <Button
              variant="outlined"
              onClick={handleReset}
              disabled={loading}
              size="large"
            >
              Reset
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Steganalysis;

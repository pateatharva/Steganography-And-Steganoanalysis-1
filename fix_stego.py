import os

# Write the clean Steganography.js file with DEBUG PANEL
content = """import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
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

function Steganography() {
  const [coverImage, setCoverImage] = useState(null);
  const [coverPreview, setCoverPreview] = useState(null);
  const [message, setMessage] = useState('');
  const [stegoImage, setStegoImage] = useState(null);
  const [stegoPreview, setStegoPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [coverMetrics, setCoverMetrics] = useState(null);
  const [stegoMetrics, setStegoMetrics] = useState(null);

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setCoverImage(file);
      setCoverPreview(URL.createObjectURL(file));
      setError('');
      setStegoImage(null);
      setStegoPreview(null);
      setCoverMetrics({ psnr: 100.0, ssim: 1.0, ber: 0.0 });
      setStegoMetrics(null);
      setSuccess('');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.bmp'] },
    multiple: false
  });

  useEffect(() => {
    return () => {
      if (coverPreview) URL.revokeObjectURL(coverPreview);
      if (stegoPreview) URL.revokeObjectURL(stegoPreview);
    };
  }, [coverPreview, stegoPreview]);

  // Debug: Monitor stegoMetrics changes
  useEffect(() => {
    console.log('🔍 stegoMetrics state changed:', stegoMetrics);
  }, [stegoMetrics]);

  // Debug: Monitor coverMetrics changes  
  useEffect(() => {
    console.log('🔍 coverMetrics state changed:', coverMetrics);
  }, [coverMetrics]);

  const handleHideMessage = async () => {
    if (!coverImage) {
      setError('Please select a cover image');
      return;
    }
    if (!message.trim()) {
      setError('Please enter a message to hide');
      return;
    }
    if (message.length > 32) {
      setError('Message must be 32 characters or less');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('image', coverImage);
      formData.append('message', message);

      console.log('📤 Sending request to backend...');

      const response = await axios.post(
        'http://127.0.0.1:5000/steganography/hide',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log('=== BACKEND RESPONSE ===');
      console.log('Full response:', response.data);
      console.log('Cover Metrics:', response.data.cover_metrics);
      console.log('Stego Metrics:', response.data.stego_metrics);

      if (response.data.success) {
        const stegoUrl = `http://127.0.0.1:5000${response.data.stego_image}`;
        setStegoImage(stegoUrl);
        setStegoPreview(stegoUrl);

        console.log('✓ Setting cover metrics:', response.data.cover_metrics);
        setCoverMetrics(response.data.cover_metrics);

        console.log('✓ Setting stego metrics:', response.data.stego_metrics);
        setStegoMetrics(response.data.stego_metrics);

        setSuccess('✅ Message hidden successfully! Check metrics below.');
      }
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.response?.data?.error || 'Failed to hide message');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCoverImage(null);
    setCoverPreview(null);
    setMessage('');
    setStegoImage(null);
    setStegoPreview(null);
    setCoverMetrics(null);
    setStegoMetrics(null);
    setError('');
    setSuccess('');
  };

  const downloadStegoImage = async () => {
    if (stegoImage) {
      try {
        const response = await fetch(stegoImage);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'stego_image.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        setError('Failed to download image');
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Image Steganography - Hide Message
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* DEBUG PANEL */}
      <Paper sx={{ p: 2, mb: 2, bgcolor: '#e3f2fd', border: '2px solid #2196f3' }}>
        <Typography variant="h6" color="primary" gutterBottom>
          🐛 DEBUG INFO
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
          coverMetrics: {coverMetrics ? JSON.stringify(coverMetrics, null, 2) : 'null'}
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', mt: 1 }}>
          stegoMetrics: {stegoMetrics ? JSON.stringify(stegoMetrics, null, 2) : 'null'}
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, fontWeight: 'bold', color: stegoMetrics ? 'success.main' : 'warning.main' }}>
          {stegoMetrics ? '✅ Stego metrics ARE in state!' : '⏳ Waiting for stego metrics...'}
        </Typography>
      </Paper>

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
              bgcolor: isDragActive ? 'action.hover' : 'background.paper'
            }}
          >
            <input {...getInputProps()} />
            {coverPreview ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Cover Image:
                </Typography>
                <img
                  src={coverPreview}
                  alt="Cover"
                  style={{ maxWidth: '100%', maxHeight: '500px', objectFit: 'contain' }}
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
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            {stegoPreview ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Stego Image (with hidden message):
                </Typography>
                <img
                  src={stegoPreview}
                  alt="Stego"
                  style={{ maxWidth: '100%', maxHeight: '500px', objectFit: 'contain' }}
                />
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={downloadStegoImage}
                  sx={{ mt: 2 }}
                >
                  Download Stego Image
                </Button>
              </Box>
            ) : (
              <Typography color="text.secondary">
                Stego image will appear here after hiding message
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Secret Message (max 32 characters)"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            variant="outlined"
            inputProps={{ maxLength: 32 }}
            helperText={`${message.length}/32 characters`}
          />
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleHideMessage}
              disabled={loading || !coverImage || !message.trim()}
              size="large"
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Stego Image'}
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

        {coverMetrics && (
          <>
            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom sx={{ mt: 3, color: 'primary.main', fontWeight: 'bold' }}>
                📊 PSNR (Peak Signal-to-Noise Ratio)
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'info.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Cover Image PSNR
                  </Typography>
                  <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                    {coverMetrics.psnr.toFixed(2)} dB
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Measured after input
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'primary.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Stego Image PSNR
                  </Typography>
                  {stegoMetrics ? (
                    <>
                      <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                        {stegoMetrics.psnr.toFixed(2)} dB
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        After generation
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body1" color="text.secondary" sx={{ my: 4 }}>
                      ⏳ Generate stego image
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom sx={{ mt: 3, color: 'success.main', fontWeight: 'bold' }}>
                📊 SSIM (Structural Similarity Index)
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'success.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="success.dark">
                    Cover Image SSIM
                  </Typography>
                  <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                    {coverMetrics.ssim.toFixed(4)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Baseline similarity
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'success.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="success.dark">
                    Stego Image SSIM
                  </Typography>
                  {stegoMetrics ? (
                    <>
                      <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                        {stegoMetrics.ssim.toFixed(4)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        After generation
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body1" color="text.secondary" sx={{ my: 4 }}>
                      ⏳ Generate stego image
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom sx={{ mt: 3, color: 'warning.dark', fontWeight: 'bold' }}>
                📊 BER (Bit Error Rate)
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'warning.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="warning.dark">
                    Cover Image BER
                  </Typography>
                  <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                    {(coverMetrics.ber * 100).toFixed(4)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expected 0%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'warning.light', height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="warning.dark">
                    Stego Image BER
                  </Typography>
                  {stegoMetrics ? (
                    <>
                      <Typography variant="h3" sx={{ my: 2, fontWeight: 'bold' }}>
                        {(stegoMetrics.ber * 100).toFixed(4)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        After generation
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body1" color="text.secondary" sx={{ my: 4 }}>
                      ⏳ Generate stego image
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
}

export default Steganography;
"""

file_path = r'c:\Users\patea\OneDrive\Desktop\Steganography And Steganoanalysis 1\frontend\src\components\Steganography.js'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File written successfully with DEBUG PANEL!")
print("✨ Refresh your browser to see the changes!")

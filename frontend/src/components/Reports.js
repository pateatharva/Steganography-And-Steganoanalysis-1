import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Chip,
  Divider
} from '@mui/material';
import { Download as DownloadIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import axios from 'axios';

function Reports() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [encodeData, setEncodeData] = useState([]);

  const fetchReports = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:5000/api/history', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const history = response.data || [];
      
      // Filter only encode operations
      setEncodeData(history.filter(item => item.operation_type === 'encode'));
      
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch reports');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatNumber = (num) => {
    return num != null ? Number(num).toFixed(4) : 'N/A';
  };

  const downloadCSV = () => {
    if (!encodeData || encodeData.length === 0) {
      alert('No data to download');
      return;
    }

    const headers = ['ID', 'Timestamp', 'Cover PSNR', 'Cover SSIM', 'Stego PSNR', 'Stego SSIM', 'BER', 'Message Length', 'Success'];
    const rows = encodeData.map(item => [
      item.id,
      formatDate(item.timestamp),
      formatNumber(item.cover_psnr),
      formatNumber(item.cover_ssim),
      formatNumber(item.stego_psnr),
      formatNumber(item.stego_ssim),
      formatNumber(item.stego_ber),
      item.message_length || 'N/A',
      item.success ? 'Yes' : 'No'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Steganography_Report.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Steganography Reports
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchReports}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={downloadCSV}
            disabled={encodeData.length === 0}
          >
            Download CSV
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {encodeData.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No steganography operations yet. Start hiding messages to see reports!
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {encodeData.map((item) => (
            <Grid item xs={12} key={item.id}>
              <Card elevation={3}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      Report ID: {item.id}
                    </Typography>
                    <Box>
                      <Chip
                        label={item.success ? 'Success' : 'Failed'}
                        color={item.success ? 'success' : 'error'}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(item.timestamp)}
                      </Typography>
                    </Box>
                  </Box>

                  <Divider sx={{ mb: 3 }} />

                  <Grid container spacing={3}>
                    {/* Cover Image Section */}
                    <Grid item xs={12} md={6}>
                      <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom color="primary">
                          Original Cover Image
                        </Typography>
                        {item.cover_path && (
                          <CardMedia
                            component="img"
                            image={`http://127.0.0.1:5000${item.cover_path}`}
                            alt="Cover Image"
                            sx={{ 
                              width: '100%', 
                              height: 400, 
                              objectFit: 'contain',
                              bgcolor: '#f5f5f5',
                              borderRadius: 1,
                              mb: 2
                            }}
                          />
                        )}
                        <Box sx={{ mt: 2 }}>
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Paper sx={{ p: 2, bgcolor: '#e3f2fd', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  PSNR
                                </Typography>
                                <Typography variant="h5" color="primary">
                                  {formatNumber(item.cover_psnr)}
                                </Typography>
                              </Paper>
                            </Grid>
                            <Grid item xs={6}>
                              <Paper sx={{ p: 2, bgcolor: '#e3f2fd', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  SSIM
                                </Typography>
                                <Typography variant="h5" color="primary">
                                  {formatNumber(item.cover_ssim)}
                                </Typography>
                              </Paper>
                            </Grid>
                          </Grid>
                        </Box>
                      </Paper>
                    </Grid>

                    {/* Stego Image Section */}
                    <Grid item xs={12} md={6}>
                      <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom color="secondary">
                          Stego Image (With Hidden Message)
                        </Typography>
                        {item.image_path && (
                          <CardMedia
                            component="img"
                            image={`http://127.0.0.1:5000${item.image_path}`}
                            alt="Stego Image"
                            sx={{ 
                              width: '100%', 
                              height: 400, 
                              objectFit: 'contain',
                              bgcolor: '#f5f5f5',
                              borderRadius: 1,
                              mb: 2
                            }}
                          />
                        )}
                        <Box sx={{ mt: 2 }}>
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Paper sx={{ p: 2, bgcolor: '#fce4ec', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  PSNR
                                </Typography>
                                <Typography variant="h5" color="secondary">
                                  {formatNumber(item.stego_psnr)}
                                </Typography>
                              </Paper>
                            </Grid>
                            <Grid item xs={6}>
                              <Paper sx={{ p: 2, bgcolor: '#fce4ec', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  SSIM
                                </Typography>
                                <Typography variant="h5" color="secondary">
                                  {formatNumber(item.stego_ssim)}
                                </Typography>
                              </Paper>
                            </Grid>
                            <Grid item xs={12}>
                              <Paper sx={{ p: 2, bgcolor: '#fff3e0', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  Bit Error Rate (BER)
                                </Typography>
                                <Typography variant="h5">
                                  {formatNumber(item.stego_ber)}
                                </Typography>
                              </Paper>
                            </Grid>
                            <Grid item xs={12}>
                              <Paper sx={{ p: 2, bgcolor: '#e8f5e9', textAlign: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                  Message Length
                                </Typography>
                                <Typography variant="h5">
                                  {item.message_length || 'N/A'}
                                </Typography>
                              </Paper>
                            </Grid>
                          </Grid>
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}

export default Reports;

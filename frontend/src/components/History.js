import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Share as ShareIcon,
  Star as StarIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [shareLink, setShareLink] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, [navigate]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login again');
        navigate('/login');
        return;
      }

      const response = await axios.get('http://127.0.0.1:5000/api/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data && Array.isArray(response.data)) {
        setHistory(response.data);
      } else {
        console.error('Invalid history data format:', response.data);
        setError('Received invalid data format from server');
      }
    } catch (error) {
      console.error('Error fetching history:', error);
      
      if (error.response?.status === 401) {
        setError('Session expired. Please login again');
        navigate('/login');
      } else if (error.message === 'Network Error') {
        setError('Network error. Please check your connection');
      } else {
        setError(error.response?.data?.error || 'Failed to load history');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://127.0.0.1:5000/api/history/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchHistory();
      setSuccess('Entry deleted successfully');
    } catch (error) {
      console.error('Error deleting entry:', error);
      setError('Failed to delete entry');
    }
  };

  const handleShare = async (item) => {
    setSelectedItem(item);
    setShareDialogOpen(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `http://127.0.0.1:5000/api/share`,
        { historyId: item.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShareLink(response.data.shareLink);
    } catch (error) {
      console.error('Error generating share link:', error);
      setError('Failed to generate share link');
    }
  };

  const handleFavorite = async (id) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://127.0.0.1:5000/api/favorites`, {
        historyId: id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('Added to favorites');
    } catch (error) {
      console.error('Error adding to favorites:', error);
      setError('Failed to add to favorites');
    }
  };

  const handleDownload = async (item) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://127.0.0.1:5000/api/download/${item.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `stego_image_${item.id}.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      setError('Failed to download file');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Processing History
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

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      ) : history.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No processing history yet. Start by hiding or extracting messages!
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Operation</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Image</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{new Date(item.timestamp).toLocaleString()}</TableCell>
                <TableCell>{item.operation_type}</TableCell>
                <TableCell>{item.success ? 'Success' : 'Failed'}</TableCell>
                <TableCell>
                  {item.image_path && (
                    <img
                      src={`http://127.0.0.1:5000${item.image_path}`}
                      alt="Stego"
                      style={{ height: '50px' }}
                    />
                  )}
                </TableCell>
                <TableCell>
                  <IconButton onClick={() => handleFavorite(item.id)}>
                    <StarIcon />
                  </IconButton>
                  <IconButton onClick={() => handleShare(item)}>
                    <ShareIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDownload(item)}>
                    <DownloadIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(item.id)}>
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      )}

      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
        <DialogTitle>Share Image</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            value={shareLink}
            label="Share Link"
            variant="outlined"
            margin="normal"
            InputProps={{
              readOnly: true,
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            navigator.clipboard.writeText(shareLink);
            setSuccess('Link copied to clipboard');
          }}>
            Copy Link
          </Button>
          <Button onClick={() => setShareDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default History;
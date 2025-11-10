import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Grid,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Divider,
  Alert,
} from '@mui/material';
import axios from 'axios';
import { toast } from 'react-toastify';

function Settings() {
  const [preferences, setPreferences] = useState({
    theme: 'light',
    notifications_enabled: true,
    max_file_size: 5242880,
    preferred_image_format: 'png'
  });

  const [apiKeys, setApiKeys] = useState([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPreferences();
    fetchApiKeys();
  }, []);

  const fetchPreferences = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/preferences', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPreferences(response.data);
    } catch (error) {
      console.error('Error fetching preferences:', error);
      toast.error('Failed to load preferences');
    }
  };

  const fetchApiKeys = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/api-keys', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys(response.data);
    } catch (error) {
      console.error('Error fetching API keys:', error);
      toast.error('Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const handlePreferenceChange = async (key, value) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put('http://localhost:5000/api/preferences', {
        [key]: value
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPreferences(prev => ({ ...prev, [key]: value }));
      toast.success('Preferences updated successfully');
    } catch (error) {
      console.error('Error updating preferences:', error);
      toast.error('Failed to update preferences');
    }
  };

  const handleGenerateApiKey = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a key name');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/api-keys', {
        name: newKeyName
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys([...apiKeys, response.data]);
      setNewKeyName('');
      toast.success('API key generated successfully');
    } catch (error) {
      console.error('Error generating API key:', error);
      toast.error('Failed to generate API key');
    }
  };

  const handleDeleteApiKey = async (keyId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:5000/api/api-keys/${keyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
      toast.success('API key deleted successfully');
    } catch (error) {
      console.error('Error deleting API key:', error);
      toast.error('Failed to delete API key');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          User Preferences
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Theme</InputLabel>
              <Select
                value={preferences.theme}
                onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                label="Theme"
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="system">System</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.notifications_enabled}
                  onChange={(e) => handlePreferenceChange('notifications_enabled', e.target.checked)}
                />
              }
              label="Enable Notifications"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Preferred Image Format</InputLabel>
              <Select
                value={preferences.preferred_image_format}
                onChange={(e) => handlePreferenceChange('preferred_image_format', e.target.value)}
                label="Preferred Image Format"
              >
                <MenuItem value="png">PNG</MenuItem>
                <MenuItem value="jpg">JPG</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              type="number"
              label="Max File Size (bytes)"
              value={preferences.max_file_size}
              onChange={(e) => handlePreferenceChange('max_file_size', parseInt(e.target.value))}
              fullWidth
            />
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          API Keys
        </Typography>
        <Box sx={{ mb: 3 }}>
          <TextField
            label="API Key Name"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            sx={{ mr: 2 }}
          />
          <Button
            variant="contained"
            onClick={handleGenerateApiKey}
            disabled={!newKeyName.trim()}
          >
            Generate New API Key
          </Button>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        {apiKeys.map((key) => (
          <Alert
            key={key.id}
            severity="info"
            sx={{ mb: 2 }}
            action={
              <Button
                color="error"
                size="small"
                onClick={() => handleDeleteApiKey(key.id)}
              >
                Delete
              </Button>
            }
          >
            <Typography variant="subtitle2">{key.name}</Typography>
            <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
              {key.key}
            </Typography>
          </Alert>
        ))}
      </Paper>
    </Box>
  );
}

export default Settings;
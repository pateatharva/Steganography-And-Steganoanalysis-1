import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Button,
  Alert,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch stats and history
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to view dashboard');
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };

      // Fetch stats and history
      const [statsRes, historyRes] = await Promise.all([
        axios.get('http://127.0.0.1:5000/api/stats', { headers }).catch((e) => ({ _error: e })),
        axios.get('http://127.0.0.1:5000/api/history', { headers }).catch((e) => ({ _error: e }))
      ]);

      if (statsRes && !statsRes._error) {
        setStats(statsRes.data);
      } else {
        console.warn('Stats fetch failed', statsRes?._error);
      }

      if (historyRes && !historyRes._error) {
        setHistory(historyRes.data || []);
      } else {
        console.warn('History fetch failed', historyRes?._error);
      }

    } catch (err) {
      console.error('Dashboard error:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    // Cleanup function
    return () => {
      setStats(null);
      setHistory([]);
    };
  }, [fetchData]);

  return (
    <Box p={3}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
            Resilient Steganography and Steganoanalysis
          </Typography>
          <Typography variant="subtitle1" gutterBottom color="textSecondary">
            A broad, robust platform for hiding, decoding and analyzing hidden data in images.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Operations</Typography>
              {loading && !stats ? (
                <CircularProgress size={28} />
              ) : (
                <Typography variant="h3">{stats?.totalOperations || 0}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Success Rate</Typography>
              {loading && !stats ? (
                <CircularProgress size={28} />
              ) : (
                <Typography variant="h3">{stats?.successRate ? `${stats.successRate}%` : '0%'}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Recent Operations</Typography>
              {loading && !stats ? (
                <CircularProgress size={28} />
              ) : (
                <Typography variant="h3">{stats?.recentOperations?.length || 0}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Activity Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Activity Overview
            </Typography>
            <Box sx={{ width: '100%', height: 300 }}>
              {history && history.length > 0 ? (
                <ResponsiveContainer>
                  <BarChart
                    data={(() => {
                      // Group operations by type and count them
                      const grouped = history.reduce((acc, item) => {
                        const type = item.operation_type || 'Unknown';
                        if (!acc[type]) {
                          acc[type] = { operation_type: type, count: 0, success: 0 };
                        }
                        acc[type].count += 1;
                        if (item.success) acc[type].success += 1;
                        return acc;
                      }, {});
                      return Object.values(grouped);
                    })()}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="operation_type" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#8884d8" name="Total" />
                    <Bar dataKey="success" fill="#82ca9d" name="Successful" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography color="textSecondary">
                    No activity data yet. Start using steganography features to see statistics!
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Activity Timeline */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Timeline>
              {(stats?.recentOperations && stats.recentOperations.length > 0) ? (
                stats.recentOperations.map((op, index) => (
                  <TimelineItem key={op.id || index}>
                    <TimelineSeparator>
                      <TimelineDot color={op.success ? 'success' : 'error'} />
                      {index < (stats.recentOperations.length - 1) && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      <Typography variant="subtitle2">{op.operation_type}</Typography>
                      <Typography variant="caption">{new Date(op.timestamp).toLocaleString()}</Typography>
                    </TimelineContent>
                  </TimelineItem>
                ))
              ) : (
                <TimelineItem>
                  <TimelineSeparator>
                    <TimelineDot />
                  </TimelineSeparator>
                  <TimelineContent>
                    <Typography variant="body2" color="textSecondary">No recent activity.</Typography>
                  </TimelineContent>
                </TimelineItem>
              )}
            </Timeline>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
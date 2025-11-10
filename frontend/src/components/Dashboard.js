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
} from 'recharts';
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
        axios.get('http://localhost:5000/api/stats', { headers }).catch((e) => ({ _error: e })),
        axios.get('http://localhost:5000/api/history', { headers }).catch((e) => ({ _error: e }))
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
      <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
        Resilient Steganography and Stegnoanalysis
      </Typography>
      <Typography variant="subtitle1" gutterBottom color="textSecondary">
        A broad, robust platform for hiding, decoding and analyzing hidden data in images.
      </Typography>
      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total Operations</Typography>
              {loading && !stats ? (
                <CircularProgress size={28} />
              ) : (
                <Typography variant="h3">{stats?.total_operations || 0}</Typography>
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
                <Typography variant="h3">{stats?.success_rate ? `${stats.success_rate.toFixed(1)}%` : '0%'}</Typography>
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
                <Typography variant="h3">{stats?.recent_operations?.length || 0}</Typography>
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
                    data={history.slice(-7)}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="operation_type" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="message_length" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ p: 2 }}>
                  <Typography color="textSecondary">No recent history to display.</Typography>
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
              {(stats?.recent_operations && stats.recent_operations.length > 0) ? (
                stats.recent_operations.map((op, index) => (
                  <TimelineItem key={op.id || index}>
                    <TimelineSeparator>
                      <TimelineDot color={op.success ? 'success' : 'error'} />
                      {index < (stats.recent_operations.length - 1) && <TimelineConnector />}
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
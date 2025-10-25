import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Sync as SyncIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

const AudioList = ({ audioFiles, onSelectAudio, onTranscribe, processingFiles }) => {
  const getStatusChip = (status) => {
    const statusConfig = {
      completed: { label: 'Completed', color: 'success', icon: <CheckIcon /> },
      processing: { label: 'Processing', color: 'info', icon: <SyncIcon /> },
      error: { label: 'Error', color: 'error', icon: <ErrorIcon /> },
      not_processed: { label: 'Not Processed', color: 'default', icon: null },
    };

    const config = statusConfig[status] || statusConfig.not_processed;
    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
        icon={config.icon}
        sx={{ minWidth: 120 }}
      />
    );
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const mb = (bytes / (1024 * 1024)).toFixed(2);
    return `${mb} MB`;
  };

  if (audioFiles.length === 0) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        No audio files found. Place audio files in the Audio directory.
      </Alert>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      {audioFiles.map((file) => (
        <Card key={file.filename} sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" component="div" gutterBottom>
                  {file.filename}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {formatDuration(file.duration)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Size: {formatFileSize(file.size)}
                  </Typography>
                </Box>
                {getStatusChip(file.status)}
              </Box>

              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                {file.status === 'processing' || processingFiles.includes(file.filename) ? (
                  <CircularProgress size={24} />
                ) : (
                  <>
                    {file.status === 'completed' && (
                      <Button
                        variant="contained"
                        startIcon={<PlayIcon />}
                        onClick={() => onSelectAudio(file)}
                      >
                        View & Play
                      </Button>
                    )}
                    {file.status === 'not_processed' && (
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => onTranscribe(file.filename)}
                      >
                        Transcribe
                      </Button>
                    )}
                  </>
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default AudioList;


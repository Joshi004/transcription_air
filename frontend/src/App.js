import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AudioList from './components/AudioList';
import AudioPlayer from './components/AudioPlayer';
import { audioAPI } from './services/api';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [audioFiles, setAudioFiles] = useState([]);
  const [selectedAudio, setSelectedAudio] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingFiles, setProcessingFiles] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    loadAudioFiles();
    checkBackendHealth();
  }, []);

  // Poll for status updates on processing files
  useEffect(() => {
    if (processingFiles.length > 0) {
      const interval = setInterval(() => {
        processingFiles.forEach((filename) => {
          checkTranscriptionStatus(filename);
        });
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(interval);
    }
  }, [processingFiles]);

  const checkBackendHealth = async () => {
    try {
      const health = await audioAPI.healthCheck();
      if (!health.models_loaded) {
        setSnackbar({
          open: true,
          message: 'Backend is starting up, models are loading...',
          severity: 'warning',
        });
      }
    } catch (err) {
      console.error('Backend health check failed:', err);
      setSnackbar({
        open: true,
        message: 'Unable to connect to backend. Make sure it is running.',
        severity: 'error',
      });
    }
  };

  const loadAudioFiles = async () => {
    try {
      setLoading(true);
      const data = await audioAPI.getAudioFiles();
      setAudioFiles(data.audio_files || []);
      setError(null);
    } catch (err) {
      console.error('Error loading audio files:', err);
      setError('Failed to load audio files. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleTranscribe = async (filename) => {
    try {
      setProcessingFiles([...processingFiles, filename]);
      const result = await audioAPI.transcribeAudio(filename);
      setSnackbar({
        open: true,
        message: `Transcription started for ${filename}. This may take 20-35 minutes.`,
        severity: 'info',
      });

      // Update file status
      setAudioFiles((prev) =>
        prev.map((file) =>
          file.filename === filename ? { ...file, status: 'processing' } : file
        )
      );
    } catch (err) {
      console.error('Error starting transcription:', err);
      setSnackbar({
        open: true,
        message: `Failed to start transcription: ${err.response?.data?.error || err.message}`,
        severity: 'error',
      });
      setProcessingFiles(processingFiles.filter((f) => f !== filename));
    }
  };

  const checkTranscriptionStatus = async (filename) => {
    try {
      const status = await audioAPI.getStatus(filename);

      if (status.status === 'completed') {
        // Remove from processing
        setProcessingFiles((prev) => prev.filter((f) => f !== filename));

        // Update file status
        setAudioFiles((prev) =>
          prev.map((file) =>
            file.filename === filename ? { ...file, status: 'completed', has_transcript: true } : file
          )
        );

        setSnackbar({
          open: true,
          message: `Transcription completed for ${filename}!`,
          severity: 'success',
        });
      } else if (status.status === 'error') {
        setProcessingFiles((prev) => prev.filter((f) => f !== filename));
        setAudioFiles((prev) =>
          prev.map((file) =>
            file.filename === filename ? { ...file, status: 'error' } : file
          )
        );

        setSnackbar({
          open: true,
          message: `Transcription failed for ${filename}: ${status.error}`,
          severity: 'error',
        });
      }
    } catch (err) {
      console.error('Error checking status:', err);
    }
  };

  const handleSelectAudio = async (file) => {
    try {
      setSelectedAudio(file);
      const transcriptData = await audioAPI.getTranscript(file.filename);
      setTranscript(transcriptData);
    } catch (err) {
      console.error('Error loading transcript:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load transcript',
        severity: 'error',
      });
    }
  };

  const handleBack = () => {
    setSelectedAudio(null);
    setTranscript(null);
    loadAudioFiles(); // Refresh list
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
            }}
          >
            <CircularProgress />
          </Box>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            🎙️ Transcription Service
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Audio transcription using Whisper Large v3
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {!selectedAudio ? (
            <AudioList
              audioFiles={audioFiles}
              onSelectAudio={handleSelectAudio}
              onTranscribe={handleTranscribe}
              processingFiles={processingFiles}
            />
          ) : (
            <AudioPlayer
              audioFile={selectedAudio}
              transcript={transcript}
              audioUrl={audioAPI.getAudioUrl(selectedAudio.filename)}
              onBack={handleBack}
            />
          )}
        </Box>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </ThemeProvider>
  );
}

export default App;

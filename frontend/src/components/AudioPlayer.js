import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Paper,
  Divider,
  Chip,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  NavigateBefore as PreviousIcon,
  NavigateNext as NextIcon,
} from '@mui/icons-material';
import CustomAudioControls from './CustomAudioControls';

const AudioPlayer = ({ audioFile, transcript, audioUrl, onBack }) => {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(null);
  const audioRef = useRef(null);
  const segmentRefs = useRef({});
  
  // Navigation state
  const [activeFilter, setActiveFilter] = useState(null);
  const [filterPosition, setFilterPosition] = useState(0);
  const [filteredSegments, setFilteredSegments] = useState([]);

  useEffect(() => {
    // Find active segment based on current time
    if (transcript && transcript.segments) {
      const index = transcript.segments.findIndex(
        (seg) => currentTime >= seg.start && currentTime < seg.end
      );
      setActiveSegmentIndex(index);

      // Auto-scroll to active segment
      if (index >= 0 && segmentRefs.current[index]) {
        segmentRefs.current[index].scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }
    }
  }, [currentTime, transcript]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSegmentClick = (startTime) => {
    if (audioRef.current) {
      audioRef.current.currentTime = startTime;
      audioRef.current.play();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getConfidenceColor = (avgLogprob) => {
    if (avgLogprob > -0.2) return '#4caf50';      // Excellent - Green
    if (avgLogprob > -0.5) return '#8bc34a';      // Good - Light Green
    if (avgLogprob > -1.0) return '#ff9800';      // Fair - Orange
    return '#f44336';                              // Poor - Red
  };

  const getConfidenceLabel = (avgLogprob) => {
    if (avgLogprob > -0.2) return 'Excellent';
    if (avgLogprob > -0.5) return 'Good';
    if (avgLogprob > -1.0) return 'Fair';
    return 'Poor';
  };

  // Navigation helper functions
  const getSegmentsByConfidence = (level) => {
    if (!transcript || !transcript.segments) return [];
    
    return transcript.segments
      .map((segment, index) => ({ segment, index }))
      .filter(({ segment }) => {
        const logprob = segment.avg_logprob || 0;
        switch (level) {
          case 'excellent': return logprob > -0.2;
          case 'good': return logprob > -0.5 && logprob <= -0.2;
          case 'fair': return logprob > -1.0 && logprob <= -0.5;
          case 'poor': return logprob <= -1.0;
          default: return false;
        }
      })
      .map(({ index }) => index);
  };

  const getConfidenceStats = () => {
    if (!transcript || !transcript.segments) return {};
    
    return {
      excellent: getSegmentsByConfidence('excellent').length,
      good: getSegmentsByConfidence('good').length,
      fair: getSegmentsByConfidence('fair').length,
      poor: getSegmentsByConfidence('poor').length,
    };
  };

  const scrollToSegment = (index) => {
    setActiveSegmentIndex(index);
    if (segmentRefs.current[index]) {
      segmentRefs.current[index].scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  };

  const handleConfidenceClick = (level) => {
    const segments = getSegmentsByConfidence(level);
    
    if (segments.length === 0) {
      return;
    }
    
    if (activeFilter === level) {
      // Already filtering this level, go to next
      const nextPosition = (filterPosition + 1) % segments.length;
      setFilterPosition(nextPosition);
      setFilteredSegments(segments);
      scrollToSegment(segments[nextPosition]);
    } else {
      // New filter, start from first segment
      setActiveFilter(level);
      setFilteredSegments(segments);
      setFilterPosition(0);
      scrollToSegment(segments[0]);
    }
  };

  const handlePreviousClick = () => {
    if (!activeFilter || filteredSegments.length === 0) return;
    
    const prevPosition = (filterPosition - 1 + filteredSegments.length) % filteredSegments.length;
    setFilterPosition(prevPosition);
    scrollToSegment(filteredSegments[prevPosition]);
  };

  const handleNextClick = () => {
    if (!activeFilter || filteredSegments.length === 0) return;
    
    const nextPosition = (filterPosition + 1) % filteredSegments.length;
    setFilterPosition(nextPosition);
    scrollToSegment(filteredSegments[nextPosition]);
  };

  const clearFilter = () => {
    setActiveFilter(null);
    setFilterPosition(0);
    setFilteredSegments([]);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      overflow: 'hidden',
      p: 2 
    }}>
      {/* Fixed Header and Audio Player */}
      <Box sx={{ flexShrink: 0 }}>
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={onBack}>
            <BackIcon />
          </IconButton>
          <Typography variant="h5">{audioFile.filename}</Typography>
        </Box>

        {/* Audio Player */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Audio Player
            </Typography>
            
            {/* Hidden Audio Element */}
            <audio
              ref={audioRef}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              src={audioUrl}
              style={{ display: 'none' }}
            >
              Your browser does not support the audio element.
            </audio>

            {/* Custom Audio Controls with Hover Tooltip */}
            <CustomAudioControls
              audioRef={audioRef}
              duration={duration}
              currentTime={currentTime}
              formatTime={formatTime}
            />
          </CardContent>
        </Card>
      </Box>

      {/* Transcript */}
      {transcript && transcript.segments && (
        <Card sx={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column',
          overflow: 'hidden',
          minHeight: 0
        }}>
          <CardContent sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            height: '100%',
            overflow: 'hidden',
            p: 2
          }}>
            {/* Fixed metadata and legend section */}
            <Box sx={{ flexShrink: 0 }}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Transcript
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Typography variant="body2" color="text.secondary">
                    Language: {transcript.language || 'Unknown'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {formatTime(transcript.duration || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Processing Time: {transcript.processing_time?.toFixed(1) || 'N/A'}s
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ mb: 2 }} />

            {/* Interactive Confidence Navigation */}
            <Box sx={{ mb: 2, p: 2, backgroundColor: 'rgba(0, 0, 0, 0.02)', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1, flexWrap: 'wrap', gap: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  Transcription Confidence - Click to navigate:
                </Typography>
                {activeFilter && (
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <IconButton size="small" onClick={handlePreviousClick} sx={{ border: '1px solid #ddd' }}>
                      <PreviousIcon fontSize="small" />
                    </IconButton>
                    <Typography variant="caption" color="text.secondary">
                      {filterPosition + 1} of {filteredSegments.length}
                    </Typography>
                    <IconButton size="small" onClick={handleNextClick} sx={{ border: '1px solid #ddd' }}>
                      <NextIcon fontSize="small" />
                    </IconButton>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      onClick={clearFilter}
                      sx={{ minWidth: 'auto', px: 1, py: 0.5 }}
                    >
                      Clear
                    </Button>
                  </Box>
                )}
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant={activeFilter === 'excellent' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleConfidenceClick('excellent')}
                  sx={{
                    borderColor: '#4caf50',
                    color: activeFilter === 'excellent' ? '#fff' : '#4caf50',
                    backgroundColor: activeFilter === 'excellent' ? '#4caf50' : 'transparent',
                    '&:hover': {
                      backgroundColor: activeFilter === 'excellent' ? '#45a049' : 'rgba(76, 175, 80, 0.1)',
                      borderColor: '#4caf50',
                    },
                  }}
                >
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#4caf50', borderRadius: 0.5, mr: 1 }} />
                  Excellent ({getConfidenceStats().excellent || 0})
                </Button>
                
                <Button
                  variant={activeFilter === 'good' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleConfidenceClick('good')}
                  sx={{
                    borderColor: '#8bc34a',
                    color: activeFilter === 'good' ? '#fff' : '#8bc34a',
                    backgroundColor: activeFilter === 'good' ? '#8bc34a' : 'transparent',
                    '&:hover': {
                      backgroundColor: activeFilter === 'good' ? '#7cb342' : 'rgba(139, 195, 74, 0.1)',
                      borderColor: '#8bc34a',
                    },
                  }}
                >
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#8bc34a', borderRadius: 0.5, mr: 1 }} />
                  Good ({getConfidenceStats().good || 0})
                </Button>
                
                <Button
                  variant={activeFilter === 'fair' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleConfidenceClick('fair')}
                  sx={{
                    borderColor: '#ff9800',
                    color: activeFilter === 'fair' ? '#fff' : '#ff9800',
                    backgroundColor: activeFilter === 'fair' ? '#ff9800' : 'transparent',
                    '&:hover': {
                      backgroundColor: activeFilter === 'fair' ? '#f57c00' : 'rgba(255, 152, 0, 0.1)',
                      borderColor: '#ff9800',
                    },
                  }}
                >
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#ff9800', borderRadius: 0.5, mr: 1 }} />
                  Fair ({getConfidenceStats().fair || 0})
                </Button>
                
                <Button
                  variant={activeFilter === 'poor' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleConfidenceClick('poor')}
                  sx={{
                    borderColor: '#f44336',
                    color: activeFilter === 'poor' ? '#fff' : '#f44336',
                    backgroundColor: activeFilter === 'poor' ? '#f44336' : 'transparent',
                    '&:hover': {
                      backgroundColor: activeFilter === 'poor' ? '#d32f2f' : 'rgba(244, 67, 54, 0.1)',
                      borderColor: '#f44336',
                    },
                  }}
                >
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#f44336', borderRadius: 0.5, mr: 1 }} />
                  Poor ({getConfidenceStats().poor || 0})
                </Button>
              </Box>
              
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Click any confidence level to jump to segments. Use arrows to navigate or click again for next.
              </Typography>
            </Box>
            </Box>

            {/* Scrollable Transcript Segments */}
            <Box sx={{ 
              flex: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              pr: 1,
              minHeight: 0
            }}>
              {transcript.segments.map((segment, index) => {
                const confidenceColor = getConfidenceColor(segment.avg_logprob || 0);
                const confidenceLabel = getConfidenceLabel(segment.avg_logprob || 0);
                const isLowConfidence = segment.avg_logprob < -1.0;
                
                return (
                  <Paper
                    key={index}
                    ref={(el) => (segmentRefs.current[index] = el)}
                    elevation={activeSegmentIndex === index ? 4 : 1}
                    sx={{
                      p: 2,
                      mb: 2,
                      cursor: 'pointer',
                      transition: 'all 0.3s',
                      backgroundColor:
                        activeSegmentIndex === index
                          ? 'rgba(25, 118, 210, 0.1)'
                          : 'background.paper',
                      borderLeft: `4px solid ${confidenceColor}`,
                      '&:hover': {
                        backgroundColor: 'rgba(0, 0, 0, 0.04)',
                      },
                    }}
                    onClick={() => handleSegmentClick(segment.start)}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {formatTime(segment.start)} - {formatTime(segment.end)}
                      </Typography>
                      {isLowConfidence && (
                        <Chip 
                          label="May be inaccurate" 
                          size="small" 
                          color="error" 
                          variant="outlined"
                          sx={{ height: 20 }}
                        />
                      )}
                    </Box>
                    <Typography variant="body1">{segment.text}</Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      Confidence: {confidenceLabel} ({segment.avg_logprob?.toFixed(2) || 'N/A'})
                    </Typography>
                  </Paper>
                );
              })}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default AudioPlayer;


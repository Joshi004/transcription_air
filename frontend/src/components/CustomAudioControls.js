import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton, Typography, Slider } from '@mui/material';
import { PlayArrow, Pause, VolumeUp } from '@mui/icons-material';

const CustomAudioControls = ({ audioRef, duration, currentTime, formatTime }) => {
  const [hoveredTime, setHoveredTime] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(1);
  const progressBarRef = useRef(null);

  // Sync play/pause state with audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);

    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);

    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
    };
  }, [audioRef]);

  const handleProgressHover = (e) => {
    if (!progressBarRef.current || !duration) return;
    
    const rect = progressBarRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const time = percentage * duration;
    
    setHoveredTime(time);
  };

  const handleProgressClick = (e) => {
    if (!progressBarRef.current || !duration || !audioRef.current) return;
    
    const rect = progressBarRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const time = percentage * duration;
    
    audioRef.current.currentTime = time;
  };

  const togglePlayPause = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  const handleVolumeChange = (e, newValue) => {
    if (!audioRef.current) return;
    audioRef.current.volume = newValue;
    setVolume(newValue);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  const hoverProgress = hoveredTime && duration > 0 ? (hoveredTime / duration) * 100 : null;

  return (
    <Box>
      {/* Play/Pause and Time Display */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <IconButton onClick={togglePlayPause} size="large" color="primary">
          {isPlaying ? <Pause /> : <PlayArrow />}
        </IconButton>
        
        <Typography variant="body2" sx={{ minWidth: '110px', fontFamily: 'monospace' }}>
          {formatTime(currentTime)} / {formatTime(duration || 0)}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto', minWidth: '150px' }}>
          <VolumeUp fontSize="small" />
          <Slider
            value={volume}
            onChange={handleVolumeChange}
            min={0}
            max={1}
            step={0.1}
            size="small"
            sx={{ width: 100 }}
          />
        </Box>
      </Box>

      {/* Custom Progress Bar with Hover Tooltip */}
      <Box sx={{ position: 'relative', py: 1 }}>
        <Box
          ref={progressBarRef}
          onMouseMove={handleProgressHover}
          onMouseLeave={() => setHoveredTime(null)}
          onClick={handleProgressClick}
          sx={{
            height: 8,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            borderRadius: 1,
            cursor: 'pointer',
            position: 'relative',
            '&:hover': {
              height: 10,
            },
            transition: 'height 0.2s',
          }}
        >
          {/* Progress Fill */}
          <Box
            sx={{
              height: '100%',
              width: `${progress}%`,
              backgroundColor: '#1976d2',
              borderRadius: 1,
              transition: 'width 0.1s',
              position: 'relative',
            }}
          />
          
          {/* Hover Indicator Line */}
          {hoverProgress !== null && (
            <Box
              sx={{
                position: 'absolute',
                left: `${hoverProgress}%`,
                top: 0,
                height: '100%',
                width: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                pointerEvents: 'none',
              }}
            />
          )}
        </Box>

        {/* Hover Tooltip */}
        {hoveredTime !== null && (
          <Box
            sx={{
              position: 'absolute',
              left: `${hoverProgress}%`,
              bottom: '120%',
              transform: 'translateX(-50%)',
              backgroundColor: 'rgba(0, 0, 0, 0.85)',
              color: 'white',
              padding: '6px 10px',
              borderRadius: 1,
              fontSize: '13px',
              fontWeight: 500,
              fontFamily: 'monospace',
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
              zIndex: 1000,
              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: '100%',
                left: '50%',
                transform: 'translateX(-50%)',
                width: 0,
                height: 0,
                borderLeft: '5px solid transparent',
                borderRight: '5px solid transparent',
                borderTop: '5px solid rgba(0, 0, 0, 0.85)',
              },
            }}
          >
            {formatTime(hoveredTime)}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default CustomAudioControls;


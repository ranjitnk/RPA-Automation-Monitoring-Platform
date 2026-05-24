import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stack,
  TextField,
  Box,
  Typography,
  Chip,
  Grid,
} from '@mui/material';

interface DrillDownModalProps {
  open: boolean;
  title: string;
  data?: Record<string, unknown>;
  onClose: () => void;
}

export const DrillDownModal: React.FC<DrillDownModalProps> = ({
  open,
  title,
  data = {},
  onClose,
}) => {
  const renderValue = (value: unknown) => {
    if (value === null || value === undefined) {
      return <Typography color="textSecondary">-</Typography>;
    }

    if (typeof value === 'boolean') {
      return <Chip label={value ? 'Yes' : 'No'} size="small" />;
    }

    if (typeof value === 'object') {
      return <pre>{JSON.stringify(value, null, 2)}</pre>;
    }

    return <Typography>{String(value)}</Typography>;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          {Object.entries(data).map(([key, value]) => (
            <Box key={key}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 0.5 }}>
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </Typography>
              {renderValue(value)}
            </Box>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

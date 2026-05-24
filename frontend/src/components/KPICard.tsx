import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  useTheme,
  Tooltip,
  Icon,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: number; // percentage change
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  description?: string;
  progress?: number; // 0-100 for progress bar
  onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  unit,
  trend,
  icon,
  color = 'primary',
  description,
  progress,
  onClick,
}) => {
  const theme = useTheme();
  const isPositiveTrend = (trend ?? 0) >= 0;

  return (
    <Card
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': onClick ? { transform: 'translateY(-4px)', boxShadow: 3 } : {},
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Typography color="textSecondary" variant="body2" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          {icon && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: 1,
                backgroundColor: `${theme.palette[color].main}20`,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          {value}
          {unit && (
            <Typography component="span" variant="body2" sx={{ ml: 0.5 }}>
              {unit}
            </Typography>
          )}
        </Typography>

        {description && (
          <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
            {description}
          </Typography>
        )}

        {progress !== undefined && (
          <Box sx={{ mb: 1 }}>
            <LinearProgress variant="determinate" value={progress} />
          </Box>
        )}

        {trend !== undefined && (
          <Tooltip title={`${isPositiveTrend ? 'Increase' : 'Decrease'} from last period`}>
            <Box display="flex" alignItems="center" gap={0.5}>
              {isPositiveTrend ? (
                <TrendingUpIcon
                  fontSize="small"
                  sx={{ color: theme.palette.success.main }}
                />
              ) : (
                <TrendingDownIcon fontSize="small" sx={{ color: theme.palette.error.main }} />
              )}
              <Typography
                variant="caption"
                sx={{
                  color: isPositiveTrend
                    ? theme.palette.success.main
                    : theme.palette.error.main,
                }}
              >
                {Math.abs(trend)}%
              </Typography>
            </Box>
          </Tooltip>
        )}
      </CardContent>
    </Card>
  );
};

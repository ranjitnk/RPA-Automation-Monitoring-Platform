import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useTheme, Box, Paper } from '@mui/material';

interface ChartDataPoint {
  [key: string]: unknown;
}

interface BaseChartProps {
  data: ChartDataPoint[];
  title?: string;
  height?: number;
}

interface LineChartProps extends BaseChartProps {
  xAxisKey: string;
  lines: Array<{
    key: string;
    stroke?: string;
    name?: string;
  }>;
}

interface BarChartProps extends BaseChartProps {
  xAxisKey: string;
  bars: Array<{
    key: string;
    fill?: string;
    name?: string;
  }>;
}

interface PieChartProps extends BaseChartProps {
  dataKey: string;
  nameKey: string;
}

const COLORS = ['#0067DF', '#FA4616', '#4caf50', '#ff9800', '#f44336', '#2196f3'];

export const ChartLineComponent: React.FC<LineChartProps> = ({
  data,
  xAxisKey,
  lines,
  height = 300,
}) => {
  const theme = useTheme();

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.palette.divider}
        />
        <XAxis dataKey={xAxisKey} stroke={theme.palette.text.secondary} />
        <YAxis stroke={theme.palette.text.secondary} />
        <Tooltip
          contentStyle={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        />
        <Legend />
        {lines.map((line, index) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            stroke={line.stroke || COLORS[index % COLORS.length]}
            name={line.name || line.key}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export const ChartBarComponent: React.FC<BarChartProps> = ({
  data,
  xAxisKey,
  bars,
  height = 300,
}) => {
  const theme = useTheme();

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.palette.divider}
        />
        <XAxis dataKey={xAxisKey} stroke={theme.palette.text.secondary} />
        <YAxis stroke={theme.palette.text.secondary} />
        <Tooltip
          contentStyle={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        />
        <Legend />
        {bars.map((bar, index) => (
          <Bar
            key={bar.key}
            dataKey={bar.key}
            fill={bar.fill || COLORS[index % COLORS.length]}
            name={bar.name || bar.key}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
};

export const ChartPieComponent: React.FC<PieChartProps> = ({
  data,
  dataKey,
  nameKey,
  height = 300,
}) => {
  const theme = useTheme();

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          dataKey={dataKey as string}
          nameKey={nameKey as string}
          cx="50%"
          cy="50%"
          outerRadius={80}
          label
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

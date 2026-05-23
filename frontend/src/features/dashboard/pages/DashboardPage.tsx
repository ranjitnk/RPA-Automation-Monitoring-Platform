import { Grid2 as Grid, Paper, Typography } from '@mui/material';

const kpis = [
  { label: 'Jobs Running', value: 0 },
  { label: 'Queue Backlog', value: 0 },
  { label: 'Robots Online', value: 0 },
  { label: 'Open SLA Breaches', value: 0 },
];

export function DashboardPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Real-time Dashboard
      </Typography>
      <Grid container spacing={2}>
        {kpis.map((kpi) => (
          <Grid key={kpi.label} size={{ xs: 12, sm: 6, md: 3 }}>
            <Paper sx={{ p: 2 }}>
              <Typography color="text.secondary">{kpi.label}</Typography>
              <Typography variant="h4">{kpi.value}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </>
  );
}

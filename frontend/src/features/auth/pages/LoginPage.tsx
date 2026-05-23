import { Button, Container, Paper, TextField, Typography } from '@mui/material';

export function LoginPage() {
  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Sign in
        </Typography>
        <TextField fullWidth label="Email" margin="normal" />
        <TextField fullWidth label="Password" type="password" margin="normal" />
        <Button variant="contained" fullWidth sx={{ mt: 2 }}>
          Login
        </Button>
      </Paper>
    </Container>
  );
}

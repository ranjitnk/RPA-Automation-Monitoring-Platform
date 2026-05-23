import { AppBar, Toolbar, Typography } from '@mui/material';

export function TopBar() {
  return (
    <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" noWrap>
          {import.meta.env.VITE_APP_TITLE ?? 'UiPath Monitor'}
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

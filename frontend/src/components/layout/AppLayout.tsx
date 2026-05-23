import { Outlet } from 'react-router-dom';
import { Box, Toolbar } from '@mui/material';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export function AppLayout() {
  return (
    <Box sx={{ display: 'flex' }}>
      <TopBar />
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}

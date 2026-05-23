import { Drawer, List, ListItemButton, ListItemText, Toolbar } from '@mui/material';
import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/queues', label: 'Queues' },
  { to: '/jobs', label: 'Jobs' },
  { to: '/robots', label: 'Robots' },
  { to: '/ai-workflows', label: 'AI Workflows' },
  { to: '/sla', label: 'SLA & Alerts' },
  { to: '/audit', label: 'Audit Logs' },
  { to: '/environments', label: 'Environments' },
];

const width = 240;

export function Sidebar() {
  return (
    <Drawer variant="permanent" sx={{ width, [`& .MuiDrawer-paper`]: { width } }}>
      <Toolbar />
      <List>
        {navItems.map((item) => (
          <ListItemButton key={item.to} component={NavLink} to={item.to}>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}

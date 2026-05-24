import { createTheme, ThemeOptions, PaletteMode } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    status: {
      success: string;
      warning: string;
      error: string;
      info: string;
    };
  }
  interface PaletteOptions {
    status?: {
      success?: string;
      warning?: string;
      error?: string;
      info?: string;
    };
  }
}

const getDesignTokens = (mode: PaletteMode): ThemeOptions => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          primary: {
            main: '#0067DF',
            light: '#4DA6FF',
            dark: '#0052B3',
          },
          secondary: {
            main: '#FA4616',
            light: '#FF6A40',
            dark: '#CC3700',
          },
          background: {
            default: '#f5f7fa',
            paper: '#ffffff',
          },
          text: {
            primary: 'rgba(0, 0, 0, 0.87)',
            secondary: 'rgba(0, 0, 0, 0.6)',
          },
          divider: 'rgba(0, 0, 0, 0.12)',
          status: {
            success: '#4caf50',
            warning: '#ff9800',
            error: '#f44336',
            info: '#2196f3',
          },
        }
      : {
          primary: {
            main: '#4DA6FF',
            light: '#7FC3FF',
            dark: '#0067DF',
          },
          secondary: {
            main: '#FF6A40',
            light: '#FF8A65',
            dark: '#FA4616',
          },
          background: {
            default: '#0f1419',
            paper: '#1a1f2e',
          },
          text: {
            primary: '#ffffff',
            secondary: 'rgba(255, 255, 255, 0.7)',
          },
          divider: 'rgba(255, 255, 255, 0.12)',
          status: {
            success: '#66bb6a',
            warning: '#ffa726',
            error: '#ef5350',
            info: '#29b6f6',
          },
        }),
  },
  typography: {
    fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 600 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
    h4: { fontSize: '1.5rem', fontWeight: 600 },
    h5: { fontSize: '1.25rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 500 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow:
            mode === 'light'
              ? '0 2px 8px rgba(0, 0, 0, 0.1)'
              : '0 2px 8px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow:
            mode === 'light'
              ? '0 2px 4px rgba(0, 0, 0, 0.1)'
              : '0 2px 4px rgba(0, 0, 0, 0.3)',
        },
      },
    },
  },
});

export default function createAppTheme(mode: PaletteMode) {
  return createTheme(getDesignTokens(mode));
}

import { createTheme } from '@mui/material/styles';

/**
 * Create theme based on mode (light or dark)
 * ChatGPT-like design with support for both modes
 */
export const createAppTheme = (mode) => createTheme({
  palette: {
    mode,
    background: {
      default: mode === 'dark' ? '#0F1115' : '#ffffff',
      paper: mode === 'dark' ? '#12141A' : '#f7f7f8',
    },
    primary: {
      main: mode === 'dark' ? '#90caf9' : '#1976d2',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#000000',
      secondary: mode === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)',
    },
    divider: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
  },
  components: {
    // Default buttons to outlined variant
    MuiButton: {
      defaultProps: {
        variant: 'outlined',
      },
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 4,
        },
        outlined: ({ theme }) => ({
          borderColor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.6)' 
            : 'rgba(0, 0, 0, 0.23)',
          color: theme.palette.text.primary,
          '&:hover': {
            borderColor: theme.palette.text.primary,
            backgroundColor: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)' 
              : 'rgba(0, 0, 0, 0.04)',
          },
        }),
      },
    },
    // Default cards to outlined variant
    MuiCard: {
      defaultProps: {
        variant: 'outlined',
      },
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 4,
          borderColor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.6)' 
            : 'rgba(0, 0, 0, 0.23)',
        }),
      },
    },
    // Text fields with outlined style
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
      },
      styleOverrides: {
        root: ({ theme }) => ({
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: theme.palette.mode === 'dark' 
                ? 'rgba(255, 255, 255, 0.6)' 
                : 'rgba(0, 0, 0, 0.23)',
            },
            '&:hover fieldset': {
              borderColor: theme.palette.text.primary,
            },
          },
        }),
      },
    },
    // Select components
    MuiSelect: {
      styleOverrides: {
        outlined: ({ theme }) => ({
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.6)' 
              : 'rgba(0, 0, 0, 0.23)',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.text.primary,
          },
        }),
      },
    },
    // List items for sidebar
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          marginBottom: 4,
          '&.Mui-selected': {
            backgroundColor: 'rgba(144, 202, 249, 0.08)',
          },
        },
      },
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Default export for backwards compatibility
const theme = createAppTheme('dark');
export default theme;

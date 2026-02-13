import { createTheme } from '@mui/material/styles';

/**
 * Create theme based on mode (light or dark)
 * ChatGPT-like design with support for both modes
 */
export const createAppTheme = (mode) => createTheme({
  palette: {
    mode,
    background: {
      default: mode === 'dark' ? '#1E1F1C' : '#F6F3ED', // Warm charcoal (dark) / Warm cream (light)
      paper: mode === 'dark' ? '#262824' : '#FBF9F5', // Soft dark slate / Soft ivory
    },
    primary: {
      main: mode === 'dark' ? '#6FB6B8' : '#4F8A8B', // Muted teal (both modes)
    },
    secondary: {
      main: mode === 'dark' ? '#7FC7A1' : '#6FAF8E', // Success green (both modes)
    },
    text: {
      primary: mode === 'dark' ? '#E8E6E1' : '#2F2F2F', // Soft off-white / Soft charcoal
      secondary: mode === 'dark' ? '#B8B4AD' : '#6E6A63', // Muted light gray / Warm gray
    },
    divider: mode === 'dark' ? '#343631' : '#DDD6CC', // Muted olive / Pale taupe
    action: {
      hover: mode === 'dark' ? '#2C302C' : '#EAE3D8',
      selected: mode === 'dark' ? '#2E3A38' : '#E2EEED',
    },
  },
  components: {
    // Paper component
    MuiPaper: {
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.palette.mode === 'dark' 
            ? '0 2px 8px rgba(0,0,0,0.4)' 
            : '0 1px 4px rgba(30,30,30,0.04)',
        }),
      },
    },
    // Typography component
    MuiTypography: {
      styleOverrides: {
        root: {
          color: 'inherit',
        },
        h4: {
          fontWeight: 700,
        },
        h6: {
          fontWeight: 700,
        },
      },
    },
    // Card content
    MuiCardContent: {
      styleOverrides: {
        root: ({ theme }) => ({
          color: theme.palette.text.primary,
        }),
      },
    },
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
            ? '#3E4440' 
            : '#DDD6CC', // Muted border in dark / Pale taupe border in light
          color: theme.palette.text.primary,
          '&:hover': {
            borderColor: theme.palette.primary.main,
            backgroundColor: theme.palette.mode === 'dark' 
              ? '#2C302C' 
              : '#EAE3D8', // Hover states
          },
        }),
        contained: ({ theme }) => ({
          backgroundColor: theme.palette.mode === 'dark' ? '#6FB6B8' : '#4F8A8B',
          color: theme.palette.mode === 'dark' ? '#1E1F1C' : '#FFFFFF',
          boxShadow: theme.palette.mode === 'dark' ? '0 2px 8px rgba(0,0,0,0.4)' : '0 6px 18px rgba(79,138,139,0.12)',
          padding: '12px 28px',
          '&:hover': {
            backgroundColor: theme.palette.mode === 'dark' ? '#5AA3A5' : '#457C7D',
            boxShadow: theme.palette.mode === 'dark' ? '0 3px 10px rgba(0,0,0,0.5)' : '0 8px 22px rgba(69,124,125,0.14)',
          },
          '&:disabled': {
            backgroundColor: theme.palette.mode === 'dark' ? '#3A5F60' : '#B8D2D3',
            color: theme.palette.mode === 'dark' ? '#8F8B83' : '#F6F8F8',
            boxShadow: 'none',
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
          borderRadius: 10,
          borderColor: theme.palette.mode === 'dark' 
            ? '#343631' 
            : '#DDD6CC', // Muted olive / Pale taupe border
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
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
            backgroundColor: theme.palette.mode === 'dark' ? '#2B2E29' : '#FFFFFF',
            borderRadius: 8,
            minHeight: 56,
            '& fieldset': {
              borderWidth: 1,
              borderColor: theme.palette.mode === 'dark' 
                ? '#3E4440' 
                : '#DDD6CC',
              transition: 'border-color 0.2s ease',
            },
            '&:hover fieldset': {
              borderWidth: 1,
              borderColor: theme.palette.mode === 'dark' 
                ? '#6FB6B8'
                : '#4F8A8B',
            },
            '&.Mui-focused fieldset': {
              borderWidth: 1.5,
              borderColor: theme.palette.mode === 'dark' 
                ? '#6FB6B8'
                : '#4F8A8B',
            },
          },
          '& .MuiInputBase-input::placeholder': {
            color: theme.palette.mode === 'dark' ? '#8F8B83' : '#9C978F',
            opacity: 0.65,
          },
        }),
      },
    },
    // Input labels
    MuiInputLabel: {
      styleOverrides: {
        root: ({ theme }) => ({
          color: theme.palette.mode === 'dark' ? '#B8B4AD' : '#6E6A63',
          '&.Mui-focused': {
            color: theme.palette.mode === 'dark' ? '#6FB6B8' : '#4F8A8B',
          },
        }),
      },
    },
    // Select components
    MuiSelect: {
      styleOverrides: {
        select: ({ theme }) => ({
          py: 1,
          minHeight: 40,
          backgroundColor: theme.palette.mode === 'dark' ? '#2B2E29' : '#FFFFFF',
        }),
        outlined: ({ theme }) => ({
          backgroundColor: theme.palette.mode === 'dark' ? '#2B2E29' : '#FFFFFF',
          borderRadius: 8,
          minHeight: 56,
          '& .MuiOutlinedInput-notchedOutline': {
            borderWidth: 1,
            borderColor: theme.palette.mode === 'dark' 
              ? '#3E4440' 
              : '#DDD6CC',
            transition: 'border-color 0.2s ease',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderWidth: 1,
            borderColor: theme.palette.mode === 'dark' 
              ? '#6FB6B8'
              : '#4F8A8B',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: 1.5,
            borderColor: theme.palette.mode === 'dark' 
              ? '#6FB6B8'
              : '#4F8A8B',
          },
        }),
      },
    },
    // List items for sidebar
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginBottom: 4,
          position: 'relative',
          '&:hover': ({ theme }) => ({
            backgroundColor: theme.palette.mode === 'dark' ? '#2C302C' : '#EAE3D8', // Hover states
          }),
          '&.MuiSelected': ({ theme }) => ({
            backgroundColor: theme.palette.mode === 'dark' ? '#2E3A38' : '#E2EEED', // Active chat background
            '&::before': {
              content: '""',
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '3px',
              backgroundColor: theme.palette.mode === 'dark' ? '#6FB6B8' : '#4F8A8B', // Muted teal accent bar
              borderRadius: '0 2px 2px 0',
            },
            '&:hover': {
              backgroundColor: theme.palette.mode === 'dark' ? '#2E3A38' : '#E2EEED',
            },
          }),
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

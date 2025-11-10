import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { 
  Container, CssBaseline, Box, Button, Typography, AppBar, Toolbar, Stack 
} from '@mui/material';
import { Height } from '@mui/icons-material';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />

  </StrictMode>,
)

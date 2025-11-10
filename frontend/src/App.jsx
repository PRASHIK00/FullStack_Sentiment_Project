import React, { useState, useEffect } from "react";
import { LoginPage } from "./pages/LoginPage.jsx";
import { EmployeeDashboard } from "./pages/EmployeeDashboard.jsx";
import { AdminDashboard } from "./pages/AdminDashboard.jsx";
import { jwtDecode } from "jwt-decode";

import {
  Container,
  CssBaseline,
  Box,
  Button,
  Typography,
  AppBar,
  Toolbar,
  Stack,
} from "@mui/material";
import { Height } from "@mui/icons-material";

const getInitialToken = () => {
  return localStorage.getItem("token");
};

function App() {
  const [token, setToken] = useState(getInitialToken());
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        setUser({
          username: decodedToken.sub,
          role: decodedToken.role,
        });
      } catch (error) {
        console.error("Invalid token", error);
        handleLogout();
      }
    } else {
      setUser(null);
    }
  }, [token]);

  const handleLoginSuccess = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  // Main Router

  if (!user) {
    return (
      <>
        <CssBaseline />
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
            backgroundColor: "#f4f4f4",
          }}
        >
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        </Box>
      </>
    );
  }

  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Driver Sentiment Dashboard
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Welcome, {user.username} ({user.role})
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <EmployeeDashboard />
        {user.role === "admin" && <AdminDashboard />}
      </Container>
    </>
  );
}

export default App;

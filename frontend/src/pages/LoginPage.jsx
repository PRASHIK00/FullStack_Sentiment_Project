import React, { useState } from "react";
import api from "../services/api";

import {
  Button,
  TextField,
  Container,
  Typography,
  Box,
  Alert,
  Paper,
  Link,
} from "@mui/material";

export const LoginPage = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const [isLoginMode, setIsLoginMode] = useState(true);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post("/token", formData);
      const token = response.data.access_token;

      localStorage.setItem("token", token);
      onLoginSuccess(token);
    } catch (err) {
      console.error("Login failed:", err);
      setError("Login failed. Check username or password.");
      localStorage.removeItem("token");
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    try {
      await api.post("/users", {
        username: username,
        password: password,
      });

      // Show success and switch to login mode
      setMessage("Account created successfully! Please sign in.");
      setIsLoginMode(true);
      setUsername("");
      setPassword("");
    } catch (err) {
      console.error("Signup failed:", err);
      // Check  server sent a error message
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Signup failed. Please try again.");
      }
    }
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError(null);
    setMessage(null);
    setUsername("");
    setPassword("");
  };

  return (
    <Container
      component="main"
      sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
      }}
    >
      <Paper elevation={3}>
        <Typography component="h1" variant="h5">
          {isLoginMode ? "Sign in" : "Sign up"}
        </Typography>

        <Box
          component="form"
          onSubmit={isLoginMode ? handleLogin : handleSignup}
          sx={{ mt: 1, width: "100%" }}
        >
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoginMode ? "Sign In" : "Create Account"}
          </Button>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}
          {message && (
            <Alert severity="success" sx={{ width: "100%", mb: 2 }}>
              {message}
            </Alert>
          )}

          <Link href="#" variant="body2" onClick={toggleMode}>
            {isLoginMode
              ? "Don't have an account? Sign Up"
              : "Already have an account? Sign In"}
          </Link>
        </Box>
      </Paper>
    </Container>
  );
};

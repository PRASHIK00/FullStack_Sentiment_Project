import React, { useState, useEffect } from "react";
import api from "../services/api";
import { FeedbackForm } from "../components/FeedbackForm.jsx";

import {
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";

export const EmployeeDashboard = () => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeForm, setActiveForm] = useState(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const response = await api.get("/config");
        setConfig(response.data);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch config:", err);
        setError("Could not load UI configuration from server.");
        setLoading(false);
      }
    };
    fetchConfig();
  }, []);

  // Render Logic

  if (loading) {
    return (
      <Paper sx={{ p: 3, display: "flex", justifyContent: "center" }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!config) {
    return null;
  }

  const enabledFeatures = config.features.filter((f) => f.enabled);

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <Typography variant="h5" component="h2" gutterBottom>
        {config.title || "Submit Feedback"}
      </Typography>

      <Box>
        <Typography variant="body1" gutterBottom align="center">
          What would you like to give feedback on?
        </Typography>
        <Box
          sx={{
            display: "flex",
            gap: 2,
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {enabledFeatures.map((feature) => (
            <Button
              key={feature.key}
              variant="contained"
              onClick={() => setActiveForm(feature)}
            >
              {feature.label}
            </Button>
          ))}
        </Box>
      </Box>

      {activeForm && (
        <Box sx={{ mt: 3, width: "100%", maxWidth: "600px" }}>
          <FeedbackForm
            entityType={activeForm.key}
            label={activeForm.label}
            onClose={() => setActiveForm(null)}
          />
        </Box>
      )}
    </Paper>
  );
};

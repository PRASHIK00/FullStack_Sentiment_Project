import React, { useState } from "react";
import api from "../services/api";

import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  Collapse,
} from "@mui/material";

export const FeedbackForm = ({ entityType, label, onClose }) => {
  const [entityId, setEntityId] = useState("");
  const [feedbackText, setFeedbackText] = useState("");
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    if (!entityId || !feedbackText) {
      setError("Please fill out both fields.");
      return;
    }

    try {
      await api.post("/feedback", {
        entity_type: entityType,
        entity_id: entityId,
        feedback_text: feedbackText,
      });

      setMessage(`${label} submitted successfully!`);
      setEntityId("");
      setFeedbackText("");

      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      console.error("Submit error:", err);
      setError("Failed to submit feedback.");
    }
  };

  const idLabel =
    entityType === "APP"
      ? "App Version (e.g., ios-v2.5)"
      : `${label.replace(" Feedback", "")} ID (e.g., D123)`;

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        border: "1px solid #ccc",
        padding: 2,
        borderRadius: 1,
        backgroundColor: "#f9f9f9",
      }}
    >
      <Typography variant="h6" gutterBottom>
        {label}
      </Typography>

      {/* Use TextField for input */}
      <TextField
        label={idLabel}
        variant="outlined"
        fullWidth
        margin="normal"
        value={entityId}
        onChange={(e) => setEntityId(e.target.value)}
      />
      <TextField
        label="Feedback"
        variant="outlined"
        fullWidth
        margin="normal"
        multiline
        rows={4}
        value={feedbackText}
        onChange={(e) => setFeedbackText(e.target.value)}
      />
      <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
        <Button type="submit" variant="contained">
          Submit
        </Button>
        <Button type="button" variant="outlined" onClick={onClose}>
          Cancel
        </Button>
      </Box>

      {/* Nice animated alerts */}
      <Collapse in={!!error}>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </Collapse>
      <Collapse in={!!message}>
        <Alert severity="success" sx={{ mt: 2 }}>
          {message}
        </Alert>
      </Collapse>
    </Box>
  );
};

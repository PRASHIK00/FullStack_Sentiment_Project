import React, { useState, useEffect } from "react";
import api from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { Paper, Typography, Box, CircularProgress, Alert } from "@mui/material";

export const AdminDashboard = () => {
  const [driverStats, setDriverStats] = useState([]);
  const [marshalStats, setMarshalStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        const [driverRes, marshalRes] = await Promise.all([
          api.get("/admin/stats/drivers"),
          api.get("/admin/stats/marshals"),
        ]);

        setDriverStats(driverRes.data);
        setMarshalStats(marshalRes.data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch admin data:", err);
        setError("Could not load admin data.");
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, []);

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

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Admin Dashboard
      </Typography>

      <Typography variant="h6">Driver Average Scores</Typography>
      <ChartComponent
        data={driverStats}
        dataKey="driver_id"
        barKey="average_score"
        fill="#8884d8"
      />

      <Typography variant="h6" sx={{ mt: 4 }}>
        Marshal Average Scores
      </Typography>
      <ChartComponent
        data={marshalStats}
        dataKey="marshal_id"
        barKey="average_score"
        fill="#82ca9d"
      />
    </Paper>
  );
};

// A reusable chart component
const ChartComponent = ({ data, dataKey, barKey, fill }) => {
  if (!data || data.length === 0) {
    return (
      <Typography variant="body2" sx={{ m: 2 }}>
        No data available to display.
      </Typography>
    );
  }

  return (
    <Box sx={{ width: "100%", height: 300, mt: 2 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={dataKey} />
          <YAxis domain={[0, 5]} />
          <Tooltip />
          <Legend />
          <Bar dataKey={barKey} fill={fill} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

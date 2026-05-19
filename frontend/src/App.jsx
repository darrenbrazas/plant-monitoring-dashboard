// react hooks for state, side effects, and caching computed values
import { useEffect, useMemo, useState } from "react";
// icons from lucide-react, one per sensor and for the ui labels
import {
  Activity,
  AlertTriangle,
  Gauge,
  RadioTower,
  Thermometer,
  Waves,
  Zap,
} from "lucide-react";
// chart.js requires you to register the features you use before rendering
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";

// getData is the only function from api.js, it calls GET /data on the backend
import { getData } from "./api";

// registering the chart.js features we imported above so they work in the Line component
ChartJS.register(
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
);

// one entry per sensor — drives both the metric cards and the charts so we don't repeat ourselves
const metricConfig = [
  {
    key: "temperature",
    label: "Temperature",
    unit: "C",
    icon: Thermometer,
    border: "#f97316",
    background: "rgba(249, 115, 22, 0.16)",
  },
  {
    key: "pressure",
    label: "Pressure",
    unit: "kPa",
    icon: Gauge,
    border: "#38bdf8",
    background: "rgba(56, 189, 248, 0.16)",
  },
  {
    key: "flow_rate",
    label: "Flow Rate",
    unit: "L/s",
    icon: Waves,
    border: "#22c55e",
    background: "rgba(34, 197, 94, 0.16)",
  },
  {
    key: "vibration",
    label: "Vibration",
    unit: "Hz",
    icon: Activity,
    border: "#a78bfa",
    background: "rgba(167, 139, 250, 0.16)",
  },
];

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 450 },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: "#0f172a",
      borderColor: "#334155",
      borderWidth: 1,
      titleColor: "#e2e8f0",
      bodyColor: "#f8fafc",
    },
  },
  scales: {
    x: {
      grid: { color: "rgba(148, 163, 184, 0.12)" },
      ticks: { color: "#94a3b8", maxRotation: 0 },
    },
    y: {
      grid: { color: "rgba(148, 163, 184, 0.12)" },
      ticks: { color: "#94a3b8" },
    },
  },
};

// converts a unix timestamp (seconds since 1970) into a readable clock time for the chart x-axis
function formatTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// renders one sensor card — colored by alert severity if an alert exists for that sensor
function MetricCard({ metric, reading }) {
  const Icon = metric.icon;
  // searches the alerts list for one matching this sensor, undefined if nothing triggered
  const alert = reading?.alerts?.find((item) => item.sensor === metric.key);

  return (
    <section className={`metric-card ${alert ? `is-${alert.severity}` : ""}`}>
      <div className="metric-card__header">
        <span className="metric-card__icon">
          <Icon size={18} />
        </span>
        <span>{metric.label}</span>
      </div>
      <strong>
        {reading ? reading[metric.key] : "--"}
        <span>{metric.unit}</span>
      </strong>
      <p>{alert ? alert.message : "Operating inside expected band"}</p>
    </section>
  );
}

// renders a 30-point line chart for one sensor using the full readings history
function MetricChart({ metric, readings }) {
  // x-axis labels are the timestamp of each reading converted to clock time
  const labels = readings.map((reading) => formatTime(reading.timestamp));
  const data = {
    labels,
    datasets: [
      {
        label: metric.label,
        data: readings.map((reading) => reading[metric.key]),
        borderColor: metric.border,
        backgroundColor: metric.background,
        borderWidth: 2,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.34,
      },
    ],
  };

  return (
    <section className="chart-panel">
      <div className="chart-panel__title">
        <span>{metric.label}</span>
        <small>{metric.unit}</small>
      </div>
      <div className="chart-panel__canvas">
        <Line options={chartOptions} data={data} />
      </div>
    </section>
  );
}

function App() {
  // readings holds the last 30 sensor snapshots, apiError holds any connection error message
  const [readings, setReadings] = useState([]);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    // mounted flag prevents state updates if the component is removed before the request finishes
    let mounted = true;

    async function pullReading() {
      try {
        const reading = await getData();
        if (!mounted) return;
        // keeps only the last 30 readings — slice(-29) takes the last 29 then adds the new one
        setReadings((current) => [...current.slice(-29), reading]);
        setApiError("");
      } catch (error) {
        if (mounted) {
          setApiError("Backend API unavailable. Start FastAPI on port 8000.");
        }
      }
    }

    // call immediately so the dashboard doesn't sit empty for the first second
    pullReading();
    // then poll every 1 second after that
    const intervalId = window.setInterval(pullReading, 1000);

    // cleanup: stop the interval when the component is removed from the page
    return () => {
      mounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  // latest is the most recent reading, used by the metric cards and plant strip
  const latest = readings.at(-1);
  // if latest is undefined (no readings yet) fall back to empty array so nothing crashes
  const activeAlerts = latest?.alerts ?? [];
  // high alerts are separated to decide between "attention" and "high alert" status
  const highAlerts = activeAlerts.filter((alert) => alert.severity === "high");

  // priority order: offline beats everything, then connecting, then high alert, then attention, then normal
  const statusLabel = useMemo(() => {
    if (apiError) return "Offline";
    if (!latest) return "Connecting";
    if (highAlerts.length) return "High Alert";
    if (activeAlerts.length) return "Attention";
    return "Normal";
  }, [activeAlerts.length, apiError, highAlerts.length, latest]);

  return (
    <main className="dashboard">
      <header className="topbar">
        <div>
          <span className="eyebrow">
            <RadioTower size={15} />
            Ontario grid simulation
          </span>
          <h1>Smart Power Plant Monitoring System</h1>
        </div>
        <div className={`system-status status-${statusLabel.toLowerCase().replace(" ", "-")}`}>
          <Zap size={18} />
          <span>{statusLabel}</span>
        </div>
      </header>

      <section className="plant-strip">
        <div>
          <span>Plant</span>
          <strong>{latest?.plant_id ?? "OPG-DARLINGTON-SIM"}</strong>
        </div>
        <div>
          <span>Generating Unit</span>
          <strong>{latest?.unit ?? "--"}</strong>
        </div>
        <div>
          <span>Output</span>
          <strong>{latest ? `${latest.output_mw} MW` : "--"}</strong>
        </div>
        <div>
          <span>Last Reading</span>
          <strong>{latest ? formatTime(latest.timestamp) : "--"}</strong>
        </div>
      </section>

      {apiError && <section className="api-error">{apiError}</section>}

      <section className="metrics-grid">
        {metricConfig.map((metric) => (
          <MetricCard key={metric.key} metric={metric} reading={latest} />
        ))}
      </section>

      <section className={`alerts-panel ${activeAlerts.length ? "has-alerts" : ""}`}>
        <div className="alerts-panel__header">
          <AlertTriangle size={19} />
          <h2>Active Alerts</h2>
        </div>
        {activeAlerts.length ? (
          <div className="alerts-list">
            {activeAlerts.map((alert) => (
              <article key={`${alert.sensor}-${alert.threshold}`} className={`alert-item ${alert.severity}`}>
                <strong>{alert.message}</strong>
                <span>
                  {alert.sensor.replace("_", " ")}: {alert.value} / threshold {alert.threshold}
                </span>
              </article>
            ))}
          </div>
        ) : (
          <p>No active anomalies detected in the latest reading.</p>
        )}
      </section>

      <section className="charts-grid">
        {metricConfig.map((metric) => (
          <MetricChart key={metric.key} metric={metric} readings={readings} />
        ))}
      </section>
    </main>
  );
}

export default App;

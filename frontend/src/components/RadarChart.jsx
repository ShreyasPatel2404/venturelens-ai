// frontend/src/components/RadarChart.jsx
// Renders a dark-themed radar chart using Recharts.
// Install: npm install recharts (already in most Vite setups)
import {
  RadarChart as RechartsRadar,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const SCORE_META = [
  { key: "market_opportunity",      short: "Market" },
  { key: "team_strength",           short: "Team" },
  { key: "product_differentiation", short: "Product" },
  { key: "traction",                short: "Traction" },
  { key: "financial_health",        short: "Finance" },
];

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs shadow-xl">
      <p className="text-amber-400 font-bold tracking-wide">{d.fullLabel}</p>
      <p className="text-white font-mono text-base font-bold">{d.value}<span className="text-gray-400 text-xs">/100</span></p>
    </div>
  );
};

/**
 * Props:
 *   scores  — { market_opportunity: 85, team_strength: 70, ... }
 *   label   — optional chart title (e.g. startup name)
 *   color   — optional stroke color (default amber)
 *   size    — "sm" | "md" | "lg" (controls height)
 */
export default function RadarChart({ scores = {}, label = "", color = "#F59E0B", size = "md" }) {
  const heights = { sm: 220, md: 300, lg: 380 };
  const height  = heights[size] || 300;

  const data = SCORE_META.map(({ key, short }) => ({
    dimension: short,
    fullLabel: SCORE_META.find(m => m.key === key)?.short + " Score",
    value:     scores[key] ?? 0,
  }));

  return (
    <div className="w-full">
      {label && (
        <p className="text-center text-xs text-gray-400 tracking-widest mb-2 font-mono uppercase">
          {label}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsRadar cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid
            stroke="#374151"
            strokeDasharray="3 3"
            gridType="polygon"
          />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "#9CA3AF", fontSize: 11, fontFamily: "DM Mono, monospace" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#4B5563", fontSize: 8 }}
            tickCount={5}
            axisLine={false}
          />
          <Radar
            data={data}
            dataKey="value"
            name={label || "Score"}
            stroke={color}
            fill={color}
            fillOpacity={0.15}
            strokeWidth={2}
            dot={{ fill: color, r: 3, strokeWidth: 0 }}
          />
          <Tooltip content={<CustomTooltip />} />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
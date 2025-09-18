import { useState } from "react";
import SacredHeader from "./SacredHeader.jsx";
import StepPanel from "./StepPanel.jsx";

export default function App() {
  const [activeId, setActiveId] = useState(null);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", color: "#e5e7eb", background: "#0b0f14", minHeight: "100vh" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px" }}>
        <h1 style={{ fontSize: 28, marginBottom: 8 }}>SACRED — Interactive Explorer</h1>
        <p style={{ opacity: 0.8, marginBottom: 24 }}>
          Click a box in the diagram to open inputs → process → outputs for that step.
        </p>

        <SacredHeader onSelect={setActiveId} />

        <StepPanel stepId={activeId} onClose={() => setActiveId(null)} />
      </div>
    </div>
  );
}

const CONTENT = {
  concept: {
    title: "Concept",
    inputs: ["Operational aim", "Stakeholders", "Initial constraints"],
    process: "Capture the concept and check it’s coherent with the wider railway ecosystem.",
    outputs: ["Concept note", "Initial ODM seed"],
  },
  step1: {
    title: "Step 1 — Concept Assurance",
    inputs: ["Route basics", "Stakeholders", "Assumptions (dimensions: frequency, night ops, rolling stock, emergencies, etc.)"],
    process: "Validate the concept; produce MoSCoW and initial Scenario Definition + high-level SOC.",
    outputs: ["MoSCoW list", "Scenario Definition (SD)", "Initial SOC bullets", "ODM v0.1"],
  },
  step2: {
    title: "Step 2 — Hazard Identification",
    inputs: ["Initial ODM", "Route walk-through", "Stakeholder interviews"],
    process: "Classify hazards by Ego/Eco; map to stakeholders; begin hazard relation & componentisation.",
    outputs: ["Hazard catalogue", "Stakeholder map", "Preliminary fault trees"],
  },
  // …fill the rest as you like…
  step7: {
    title: "Step 7 — Safe Operating Context",
    inputs: ["Metrics & thresholds", "TRAP playbooks", "Tech constraints from Step 6"],
    process: "Set explicit, checkable operating bounds + degraded modes.",
    outputs: ["SOC table", "SOC narrative", "Assurance hooks (evidence to collect)"],
  },
};

export default function StepPanel({ stepId, onClose }) {
  if (!stepId) return null;
  const data = CONTENT[stepId] || { title: stepId, inputs: [], process: "", outputs: [] };

  return (
    <div style={{ marginTop: 24, background: "#111827", border: "1px solid #374151", borderRadius: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid #374151" }}>
        <h2 style={{ margin: 0, fontSize: 22 }}>{data.title}</h2>
        <button onClick={onClose} style={{ background: "transparent", color: "#9CA3AF", border: "1px solid #4B5563", borderRadius: 8, padding: "6px 10px", cursor: "pointer" }}>
          Close
        </button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, padding: 20 }}>
        <InfoCard heading="Inputs" items={data.inputs} />
        <InfoCard heading="Outputs" items={data.outputs} />
        <div style={{ gridColumn: "1 / -1" }}>
          <h3 style={{ margin: "12px 0 6px", fontSize: 16, color: "#d1d5db" }}>Process</h3>
          <p style={{ margin: 0, opacity: 0.9 }}>{data.process}</p>
        </div>
      </div>
    </div>
  );
}

function InfoCard({ heading, items }) {
  return (
    <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 10, padding: 14 }}>
      <h3 style={{ margin: "0 0 8px", fontSize: 16, color: "#d1d5db" }}>{heading}</h3>
      {items && items.length ? (
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {items.map((t, i) => (
            <li key={i} style={{ marginBottom: 6 }}>{t}</li>
          ))}
        </ul>
      ) : (
        <p style={{ margin: 0, opacity: 0.8 }}>—</p>
      )}
    </div>
  );
}

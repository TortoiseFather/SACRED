// A simple header that shows your diagram as an image
// and lays absolute-positioned buttons over the boxes.

const HOTSPOTS = [
  // id, label, top%, left%, width%, height%
  // Tweak these numbers until buttons sit on your boxes.
  { id: "concept",     label: "Concept",                  top: 83, left: 9,  w: 10, h: 10 },
  { id: "step1",       label: "1. Concept Assurance",     top: 45, left: 20, w: 12, h: 10 },
  { id: "step2",       label: "2. Hazard Identification", top: 45, left: 34, w: 14, h: 10 },
  { id: "egoHaz",      label: "EGO Hazard Analysis",      top: 66, left: 29, w: 12, h: 9  },
  { id: "ecoHaz",      label: "ECO Hazard Analysis",      top: 66, left: 39, w: 12, h: 9  },
  { id: "compId",      label: "Identification of components", top: 84, left: 33, w: 18, h: 10 },
  { id: "step3",       label: "3. Requirements / Assurance", top: 45, left: 48, w: 15, h: 10 },
  { id: "incidents",   label: "Incident Reports",         top: 30, left: 46, w: 12, h: 9  },
  { id: "reactions",   label: "Reaction Capturing",       top: 30, left: 58, w: 12, h: 9  },
  { id: "step4",       label: "4. Metric Classification", top: 14, left: 52, w: 14, h: 10 },
  { id: "criticality", label: "Criticality Determination", top: 11, left: 66, w: 16, h: 10 },
  { id: "odmVerify",   label: "ODM Verification",         top: 24, left: 66, w: 14, h: 10 },
  { id: "step5",       label: "5. Failure Management",    top: 61, left: 68, w: 14, h: 10 },
  { id: "step6",       label: "6. AS Design Assurance",   top: 61, left: 79, w: 14, h: 10 },
  { id: "step7",       label: "7. Safe Operating Context", top: 61, left: 91, w: 16, h: 10 },
];

export default function SacredHeader({ onSelect }) {
  return (
    <div style={{ position: "relative", width: "100%", borderRadius: 12, overflow: "hidden", boxShadow: "0 10px 30px rgba(0,0,0,0.35)" }}>
      <img
        src="/SACRED.svg"
        alt="SACRED methodology overview"
        style={{ width: "100%", height: "auto", display: "block" }}
        draggable={false}
      />
      {HOTSPOTS.map(({ id, label, top, left, w, h }) => (
        <button
          key={id}
          title={label}
          aria-label={label}
          onClick={() => onSelect(id)}
          style={{
            position: "absolute",
            top: `${top}%`,
            left: `${left}%`,
            width: `${w}%`,
            height: `${h}%`,
            transform: "translate(-50%, -50%)",
            cursor: "pointer",
            // visual affordance on hover/focus:
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.25)",
            borderRadius: 10,
            outline: "none",
          }}
          onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.12)")}
          onMouseLeave={e => (e.currentTarget.style.background = "rgba(255,255,255,0.06)")}
          onFocus={e => (e.currentTarget.style.boxShadow = "0 0 0 2px #fbbf24")}
          onBlur={e => (e.currentTarget.style.boxShadow = "none")}
        />
      ))}
    </div>
  );
}

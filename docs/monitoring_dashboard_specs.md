# Monitoring Dashboard Specs

**Version:** 1.0.0  
**Theme:** Light only · Soft neutrals · Glassmorphism + Claymorphism  

---

## 1. Design principles

- No dark mode.
- Soft neutral palette (slate / stone grays, white surfaces).
- Glass panels: translucent white + backdrop blur + light border.
- Clay cards: soft dual-direction shadow (neumorphic feel) for KPI tiles and model cards.
- Typography: Inter, 400–600 weights.
- Avoid saturated “AI gradient” colors; accent is muted slate.

## 2. Pages

| Page | Primary content |
|------|-----------------|
| **Overview** | 4 KPI clay cards, 24h performance chart (AUC + latency), recent events, pipeline health chips |
| **Drift** | KPI row (monitored / detected / threshold / last check), PSI table with status badges |
| **Models** | Registry cards with metrics, stage badge, Promote / Retrain actions |
| **Pipelines** | Recent run history (API-backed when live) |
| **Alerts** | Active drift / performance alerts |

## 3. Visual tokens

| Token | Value |
|-------|-------|
| Background | `#f4f5f7` |
| Surface glass | `rgba(255,255,255,0.72)` + blur 16–20px |
| Text primary | `#1e293b` |
| Text muted | `#94a3b8` |
| Success / Watch / Drift | emerald / amber / red (soft backgrounds) |
| Radius | 16px panels, 12px cards |
| Shadow clay | `8px 8px 20px rgba(15,23,42,0.06), -6px -6px 16px rgba(255,255,255,0.9)` |

## 4. Data sources

- Live: FastAPI `GET /overview`, `/drift`, `/models`
- Offline fallback: mock payloads in `frontend/js/api.js` so GitHub Pages remains usable.

## 5. Figma

Design file: [Realtime MLOps Platform — Monitoring Dashboard](https://www.figma.com/design/0KfsVcmjZeh7Fm9Dkg6yud/Realtime-MLOps-Platform---Monitoring-Dashboard)

Pages mapped: Overview · Drift · Models (see README Design section).

## 6. Accessibility

- Contrast ≥ 4.5:1 for body text.
- Focus states on nav and buttons.
- Chart tooltips keyboard-accessible via Chart.js defaults.

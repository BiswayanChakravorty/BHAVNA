# BHAVNA

## Brutally honest AI decision audits for products and businesses

BHAVNA helps founders, product teams, and e-commerce operators pressure-test an idea before spending heavily on it. Upload the evidence—product briefs, customer interviews, competitor notes, reviews, pricing hypotheses, launch plans, or market research—and describe the decision you are considering.

BHAVNA builds a structured simulation of customers, non-buyers, competitors, operators, channels, regulators, investors, and skeptics. It then runs an adversarial audit that asks the uncomfortable questions a friendly advisor may avoid:

- Is the problem painful enough to pay for?
- Will the public trust and accept the product?
- Can it scale without operational or economic collapse?
- Can competitors and substitutes erase the advantage?
- What assumption is most likely to kill the launch?

The output is a detailed audit report with scores from **0–10** for:

1. Scalability
2. Public acceptance
3. Problem–solution fit
4. Defensibility
5. Economics

It also provides an overall score, a **LAUNCH / PILOT / REWORK / KILL** recommendation, the strongest case against the idea, evidence gaps, and concrete tests for the next 72 hours.

## The 5,000-agent panel

BHAVNA uses a declared **5,000-agent panel design** across stratified role groups. This is a batched panel-synthesis architecture, not a claim that every audit makes 5,000 separate paid LLM calls. The panel target gives the audit a consistent coverage model while keeping cost and latency bounded. The report displays the panel size and method so users can distinguish design scale from measured evidence.

BHAVNA is a decision aid, not a guarantee of commercial success. Scores are only as strong as the evidence supplied and the quality of the simulation. Sensitive customer, financial, medical, or personal data should be anonymized before upload.

## Architecture

- **Frontend:** Vue/Vite application deployable to GitHub Pages.
- **Simulation backend:** Python Flask API using the existing graph, memory, and social-simulation components.
- **Audit layer:** BHAVNA adversarial scoring service with structured JSON output and persisted audit metadata.
- **LLM:** any OpenAI-compatible provider.
- **Memory:** Zep Cloud.
- **Deployment:** GitHub Pages for the frontend and Render, Docker, or another Python host for the backend.

The original simulation components are retained under the project’s AGPL-3.0 obligations. BHAVNA’s product layer, audit rubric, prompts, and branding are independent additions. See `LICENSE` and `BHAVNA_DEPLOYMENT.md`.

## Run locally

```bash
cp .env.example .env
# Set LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME, and ZEP_API_KEY
npm run setup:all
npm run dev
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

To change the declared panel size for a controlled deployment, set:

```bash
BHAVNA_AGENT_PANEL_SIZE=5000
```

The default is 5,000. Increasing the declared panel size does not automatically create one LLM call per agent.

## Deploy

See [BHAVNA_DEPLOYMENT.md](./BHAVNA_DEPLOYMENT.md) for the GitHub Pages workflow, backend deployment blueprint, environment variables, and security notes.

GitHub Pages cannot execute the Python simulation backend or hold private LLM/Zep keys. The backend must run separately, and the frontend must receive its public HTTPS URL through `VITE_API_BASE_URL`.

## Attribution

BHAVNA uses and adapts open-source components from the MiroFish project and OASIS. Their licenses and notices remain in this repository. BHAVNA does not claim ownership of upstream code, names, or marks.

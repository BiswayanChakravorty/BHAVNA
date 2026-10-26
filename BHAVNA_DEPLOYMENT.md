# BHAVNA deployment

BHAVNA is the business and e-commerce testing entry point for MiroFish. The upstream MiroFish application remains intact: users upload seed material such as a product brief, customer research, competitor notes, policy draft, or market report, then describe the scenario they want simulated.

## Architecture

- **Frontend:** Vue/Vite, deployed to GitHub Pages by `.github/workflows/deploy-pages.yml`.
- **Backend:** the existing Python MiroFish API, deployed as a Docker web service using `render.yaml` or `docker compose`.
- **LLM:** any OpenAI-compatible provider. The default example uses Alibaba Qwen-plus.
- **Memory:** Zep Cloud, configured with `ZEP_API_KEY`.

GitHub Pages is static hosting. It cannot execute the Python backend, run OASIS simulations, or safely hold LLM/Zep secrets. Do not put API keys in frontend code or GitHub Pages variables that are exposed to the browser.

## Deploy the backend

1. Push this repository to GitHub.
2. In Render, create a new **Blueprint** from this repository. Render reads `render.yaml`.
3. Set `LLM_API_KEY` and `ZEP_API_KEY` as secret environment variables.
4. Wait for the service to become healthy and copy its HTTPS URL.
5. In the GitHub repository, open **Settings → Pages** and select **GitHub Actions** as the source.
6. In **Settings → Secrets and variables → Actions → Variables**, create `VITE_API_BASE_URL` with the backend URL, for example `https://bhavna-mirofish.onrender.com`.
7. Push to `main` or run **Deploy MiroFish frontend to GitHub Pages** manually.

The public Pages URL is normally `https://<github-owner>.github.io/<repository-name>/`.

## Local full-stack run

```bash
cp .env.example .env
# Set LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME and ZEP_API_KEY
npm run setup:all
npm run dev
```

For local frontend development against a remote backend:

```bash
cd frontend
VITE_API_BASE_URL=https://your-backend.example.com npm run dev
```

## Business and product scenarios

Useful seed material includes product specifications, customer interview notes, competitor comparisons, ad concepts, pricing hypotheses, launch plans, reviews, and market research. Prompts can ask the simulated agents to explore demand, objections, price sensitivity, positioning, launch reactions, retention risks, channel mix, or competitor responses.

Treat outputs as scenario exploration, not guaranteed forecasts. Simulations consume LLM tokens, and sensitive customer or financial data should be removed or anonymized before upload.

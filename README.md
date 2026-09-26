# Heathrow Surface Access Explorer

A coursework dashboard deployed to GitHub Pages using Stlite.

## Deploy to GitHub Pages

1. In this repository, open **Settings → Pages** and select **GitHub Actions** as the source.
2. Leave **Custom domain** empty to inherit the domain configured on `majdyousof.github.io`.
3. Commit the changes and push or merge them into the default branch.
4. In **Actions**, wait for the **GitHub Pages** workflow to finish.

Expected address: **https://www.majdyousof.com/imperialgroupproject/**

You can also start the workflow manually from **Actions → GitHub Pages → Run workflow**, selecting the default branch.

## Preview locally

From the repository root:

```bash
python3 -m heathrow.build_site --base-path /
python3 -m http.server 8000 --directory dist
```

Open **http://127.0.0.1:8000/**. Internet access is required for the browser runtime, packages and map tiles.

Use the sidebar to navigate during local preview; direct subpage refreshes require the GitHub Pages fallback.

Rebuild after editing app files, then refresh the browser. Stop the preview server with **Ctrl+C**. The generated `dist/` directory is ignored by Git; the deployment workflow builds it automatically.

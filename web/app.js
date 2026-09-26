// Resolve assets from this module, including after a subpage refresh.
const baseUrl = new URL(".", import.meta.url);
const container = document.getElementById("app");

try {
  const route = new URL(baseUrl);
  route.search = location.search;
  route.searchParams.delete("__route");
  route.hash = location.hash;
  const restoredRoute = new URLSearchParams(location.search).get("__route");
  let destination = route;
  if (restoredRoute) {
    const target = new URL(restoredRoute, location.origin);
    if (target.origin === baseUrl.origin && target.pathname.startsWith(baseUrl.pathname)) {
      destination = target;
    }
  }

  const response = await fetch(new URL("stlite.json", baseUrl), {
    signal: AbortSignal.timeout(30_000),
    cache: "no-cache",
  });
  if (!response.ok) throw new Error(`Stlite configuration: HTTP ${response.status}`);
  const { runtimeVersion, ...options } = await response.json();
  const runtimeUrl = `https://cdn.jsdelivr.net/npm/@stlite/browser@${runtimeVersion}/build/`;
  const stylesheet = document.createElement("link");
  stylesheet.rel = "stylesheet";
  stylesheet.href = `${runtimeUrl}stlite.css`;
  const stylesReady = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("Stylesheet loading timed out")), 30_000);
    stylesheet.onload = () => { clearTimeout(timer); resolve(); };
    stylesheet.onerror = () => { clearTimeout(timer); reject(new Error("Stylesheet failed to load")); };
  });
  document.head.append(stylesheet);

  const [{ mount }] = await Promise.all([import(`${runtimeUrl}stlite.js`), stylesReady]);
  // Stlite 1.8.1's browser mount() derives its base path from location.pathname;
  // it does not forward the kernel's basePath option. Mount at the app root,
  // then restore the requested route before React renders the navigation.
  history.replaceState(null, "", route.href);
  // Stlite owns asynchronous worker/package errors and displays its error toasts.
  // The catch below handles failures of this initial HTML/JS/CSS loader only.
  mount(options, container);
  history.replaceState(null, "", destination.href);
} catch (error) {
  console.error("Unable to load the Heathrow dashboard", error);
  const message = document.createElement("div");
  message.id = "startup";
  message.setAttribute("role", "alert");
  message.textContent = "The dashboard loader could not start. Check your connection and reload the page.";
  const retry = document.createElement("a");
  retry.href = baseUrl.href;
  retry.textContent = "Reload dashboard";
  message.append(document.createElement("br"), retry);
  container.replaceChildren(message);
}

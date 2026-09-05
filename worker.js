export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Proxy /api/* requests to the Oracle backend
    if (url.pathname.startsWith("/api/")) {
      const backendUrl = `http://140.245.241.54:8080${url.pathname}${url.search}`;
      return fetch(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      });
    }

    // Serve static assets for everything else
    return env.ASSETS.fetch(request);
  },
};

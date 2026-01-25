// Cloudflare Worker - Keep Backend Alive
// Pings backend every 2 minutes to prevent Render free tier from sleeping

const BACKEND_URL = 'https://tvet-quiz-backend.onrender.com/health';

export default {
  async scheduled(event, env, ctx) {
    try {
      const response = await fetch(BACKEND_URL, {
        method: 'GET',
        headers: { 'User-Agent': 'KeepAlive-Worker' }
      });
      
      console.log(`✅ Ping successful: ${response.status} at ${new Date().toISOString()}`);
    } catch (error) {
      console.error(`❌ Ping failed: ${error.message}`);
    }
  },

  async fetch(request) {
    return new Response('Keep-Alive Worker Running ✅\nPinging backend every 2 minutes.', {
      headers: { 'Content-Type': 'text/plain' }
    });
  }
};

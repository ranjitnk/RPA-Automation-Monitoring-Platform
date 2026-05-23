const wsBase = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/api/v1/realtime/ws';

export function connectRealtime(token: string, environmentId: string): WebSocket {
  const url = `${wsBase}?token=${encodeURIComponent(token)}&environment_id=${environmentId}`;
  return new WebSocket(url);
}

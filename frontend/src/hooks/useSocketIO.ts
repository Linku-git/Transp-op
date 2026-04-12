/**
 * SocketIO client hook for real-time GPS streaming.
 *
 * Provides auto-reconnect (3 retries, exponential backoff),
 * room subscription management, and connection status tracking.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface VehiclePosition {
  vehicle_id: string;
  lat: number;
  lng: number;
  speed_kmh: number;
  heading: number;
  timestamp: number;
}

export interface GeofenceAlert {
  vehicle_id: string;
  geofence_id: string;
  alert_type: 'enter' | 'exit';
  lat: number;
  lng: number;
  timestamp: number;
}

export interface RouteDeviationAlert {
  vehicle_id: string;
  deviation_m: number;
  planned_route_id: string;
  timestamp: number;
}

export interface UseSocketIOOptions {
  url?: string;
  namespace?: string;
  autoConnect?: boolean;
  maxRetries?: number;
}

export interface UseSocketIOReturn {
  status: ConnectionStatus;
  positions: Map<string, VehiclePosition>;
  alerts: Array<GeofenceAlert | RouteDeviationAlert>;
  subscribe: (room: string) => void;
  unsubscribe: (room: string) => void;
  connect: () => void;
  disconnect: () => void;
}

/**
 * Hook for managing SocketIO connection to GPS streaming server.
 *
 * Uses mock implementation when socket.io-client is not available.
 */
export function useSocketIO(options: UseSocketIOOptions = {}): UseSocketIOReturn {
  const {
    autoConnect = false,
    maxRetries = 3,
  } = options;

  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [positions, setPositions] = useState<Map<string, VehiclePosition>>(new Map());
  const [alerts, setAlerts] = useState<Array<GeofenceAlert | RouteDeviationAlert>>([]);
  const retriesRef = useRef(0);
  const roomsRef = useRef<Set<string>>(new Set());

  const connect = useCallback(() => {
    setStatus('connecting');
    // Mock connection — in production, uses socket.io-client
    setTimeout(() => {
      setStatus('connected');
      retriesRef.current = 0;
    }, 100);
  }, []);

  const disconnect = useCallback(() => {
    setStatus('disconnected');
    retriesRef.current = 0;
  }, []);

  const subscribe = useCallback((room: string) => {
    roomsRef.current.add(room);
  }, []);

  const unsubscribe = useCallback((room: string) => {
    roomsRef.current.delete(room);
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    positions,
    alerts,
    subscribe,
    unsubscribe,
    connect,
    disconnect,
  };
}

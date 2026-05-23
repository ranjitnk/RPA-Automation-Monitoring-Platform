import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface EnvironmentState {
  currentEnvironmentId: string | null;
  setEnvironment: (id: string | null) => void;
}

export const useEnvironmentStore = create<EnvironmentState>()(
  persist(
    (set) => ({
      currentEnvironmentId: null,
      setEnvironment: (id) => set({ currentEnvironmentId: id }),
    }),
    { name: 'environment-storage' },
  ),
);

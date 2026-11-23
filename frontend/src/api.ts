import type {
  ConfigOptionsResponse,
  OrganismSnapshot,
  RegistryResponse,
  ScalePreset,
  ScenarioPreset,
  SeedTemplate,
  ShockType,
} from './types';

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, init);
  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(errText || `HTTP ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  getState: () => jsonFetch<OrganismSnapshot>('/api/state'),
  getRegistry: () => jsonFetch<RegistryResponse>('/api/registry'),
  getOptions: () => jsonFetch<ConfigOptionsResponse>('/api/config/options'),
  configure: (payload: {
    seed_template: SeedTemplate;
    scale_preset: ScalePreset;
    scenario_preset: ScenarioPreset;
    rng_seed?: number;
    imported_spore_seed?: Record<string, unknown> | null;
  }) =>
    jsonFetch<OrganismSnapshot>('/api/sim/configure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  step: (steps: number) =>
    jsonFetch<OrganismSnapshot>('/api/sim/step', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ steps }),
    }),
  triggerShock: (shock_type: ShockType, duration_days = 10, intensity = 0.8) =>
    jsonFetch<OrganismSnapshot>('/api/sim/shock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shock_type, duration_days, intensity }),
    }),
  gardenerAction: (payload: Record<string, unknown>) =>
    jsonFetch<{ snapshot: OrganismSnapshot; exported_spore_seed: Record<string, unknown> | null }>(
      '/api/gardener/action',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      },
    ),
  labMutate: (payload: Record<string, unknown>) =>
    jsonFetch<OrganismSnapshot>('/api/lab/mutate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
};

import { api } from './client';
import type {
  Scenario,
  ScenarioComparison,
  ScenarioRequest,
  WeatherForecast,
  WeatherSuggestions,
} from '../types/scenario';

const BASE_PATH = '/api/v1/scenarios';
const WEATHER_PATH = '/api/v1/weather';

export const simulateScenario = async (
  params: ScenarioRequest,
): Promise<Scenario> => {
  const response = await api.post<Scenario>(`${BASE_PATH}/simulate`, params);
  return response.data;
};

export const listScenarios = async (
  siteId?: string,
  page: number = 1,
  pageSize: number = 20,
): Promise<Scenario[]> => {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (siteId) params.site_id = siteId;
  const response = await api.get<Scenario[]>(BASE_PATH, { params });
  return response.data;
};

export const getScenario = async (id: string): Promise<Scenario> => {
  const response = await api.get<Scenario>(`${BASE_PATH}/${id}`);
  return response.data;
};

export const deleteScenario = async (id: string): Promise<void> => {
  await api.delete(`${BASE_PATH}/${id}`);
};

export const compareScenarios = async (
  scenarioIds: string[],
): Promise<ScenarioComparison> => {
  const response = await api.post<ScenarioComparison>(`${BASE_PATH}/compare`, {
    scenario_ids: scenarioIds,
  });
  return response.data;
};

export const getWeatherForecasts = async (
  siteId: string,
): Promise<WeatherForecast[]> => {
  const response = await api.get<WeatherForecast[]>(
    `${WEATHER_PATH}/${siteId}`,
  );
  return response.data;
};

export const refreshWeather = async (
  siteId: string,
): Promise<{ site_id: string; forecasts_updated: number }> => {
  const response = await api.post<{
    site_id: string;
    forecasts_updated: number;
  }>(`${WEATHER_PATH}/${siteId}/refresh`);
  return response.data;
};

export const getWeatherSuggestions = async (
  siteId: string,
): Promise<WeatherSuggestions> => {
  const response = await api.get<WeatherSuggestions>(
    `${WEATHER_PATH}/${siteId}/suggestions`,
  );
  return response.data;
};

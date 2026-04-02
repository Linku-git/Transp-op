import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { getWeatherForecasts, getWeatherSuggestions, refreshWeather } from '@/api/scenarios';
import type { WeatherForecast, ScenarioSuggestion } from '@/types/scenario';

interface WeatherWidgetProps {
  siteId: string;
  onCreateScenario?: (conditionType: string) => void;
}

const CONDITION_ICONS: Record<string, string> = {
  Clear: '\u2600\uFE0F',
  Clouds: '\u2601\uFE0F',
  Rain: '\uD83C\uDF27\uFE0F',
  Drizzle: '\uD83C\uDF26\uFE0F',
  Snow: '\u2744\uFE0F',
  Thunderstorm: '\u26C8\uFE0F',
  default: '\uD83C\uDF24\uFE0F',
};

function getConditionIcon(condition: string | null): string {
  if (!condition) return CONDITION_ICONS.default;
  for (const [key, icon] of Object.entries(CONDITION_ICONS)) {
    if (key !== 'default' && condition.toLowerCase().includes(key.toLowerCase())) {
      return icon;
    }
  }
  return CONDITION_ICONS.default;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

function SkeletonCard() {
  return (
    <div className="bg-white/10 rounded-xl p-3 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-md bg-white/20" />
        <div className="flex-1 space-y-1.5">
          <div className="h-3 w-20 rounded bg-white/20" />
          <div className="h-3 w-28 rounded bg-white/20" />
        </div>
        <div className="h-5 w-12 rounded bg-white/20" />
      </div>
    </div>
  );
}

export function WeatherWidget({ siteId, onCreateScenario }: WeatherWidgetProps) {
  const { t } = useTranslation();

  const [forecasts, setForecasts] = useState<WeatherForecast[]>([]);
  const [suggestions, setSuggestions] = useState<ScenarioSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (site: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [forecastData, suggestionData] = await Promise.all([
        getWeatherForecasts(site),
        getWeatherSuggestions(site),
      ]);
      setForecasts(forecastData);
      setSuggestions(suggestionData.suggestions);
    } catch {
      setError(t('weather.fetch_error', 'Unable to load weather data'));
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  useEffect(() => {
    if (siteId) {
      fetchData(siteId);
    }
  }, [siteId, fetchData]);

  const handleRefresh = useCallback(async () => {
    if (!siteId || isRefreshing) return;
    setIsRefreshing(true);
    try {
      await refreshWeather(siteId);
      await fetchData(siteId);
    } catch {
      setError(t('weather.refresh_error', 'Failed to refresh weather'));
    } finally {
      setIsRefreshing(false);
    }
  }, [siteId, isRefreshing, fetchData, t]);

  const getSuggestionForDate = useCallback(
    (date: string): ScenarioSuggestion | undefined => {
      return suggestions.find((s) => s.date === date);
    },
    [suggestions],
  );

  // Empty state: no siteId
  if (!siteId) {
    return (
      <div className="bg-gradient-to-br from-blue-500 to-primary-container text-white rounded-2xl shadow-lg p-5">
        <p className="text-sm font-sans text-white/80 text-center">
          {t('weather.select_site', 'Select a site to view weather forecast')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-500 to-primary-container text-white rounded-2xl shadow-lg p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-sans text-sm font-bold text-white">
          {t('weather.title', 'Weather Forecast')}
        </h3>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing || isLoading}
          className="p-1.5 rounded-md text-white/70 hover:bg-white/10 transition-colors duration-150 disabled:opacity-40"
          title={t('weather.refresh', 'Refresh')}
        >
          <svg
            className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-2.5">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {/* Error state */}
      {!isLoading && error && (
        <div className="bg-white/10 rounded-xl p-3 text-center">
          <p className="text-xs font-sans text-white/80">
            {error}
          </p>
          <button
            onClick={() => fetchData(siteId)}
            className="mt-2 text-xs font-sans font-medium text-white hover:underline"
          >
            {t('common.retry', 'Retry')}
          </button>
        </div>
      )}

      {/* Empty state: no forecasts */}
      {!isLoading && !error && forecasts.length === 0 && (
        <div className="bg-white/10 rounded-xl p-3 text-center">
          <p className="text-xs font-sans text-white/80">
            {t('weather.no_data', 'No forecast data available')}
          </p>
        </div>
      )}

      {/* Forecast cards */}
      {!isLoading && !error && forecasts.length > 0 && (
        <div className="space-y-2.5">
          {forecasts.map((forecast) => {
            const suggestion = getSuggestionForDate(forecast.date);

            return (
              <div
                key={forecast.id}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-3"
              >
                {/* Day row: icon + info + temps */}
                <div className="flex items-start gap-3">
                  {/* Condition icon */}
                  <span className="text-2xl leading-none mt-0.5" role="img" aria-label={forecast.condition_summary ?? 'weather'}>
                    {getConditionIcon(forecast.condition_summary)}
                  </span>

                  {/* Date and condition */}
                  <div className="flex-1 min-w-0">
                    <p className="font-sans text-xs font-medium text-white">
                      {formatDate(forecast.date)}
                    </p>
                    <p className="text-xs font-sans text-white/70 mt-0.5 truncate">
                      {forecast.condition_summary ?? t('weather.unknown', 'Unknown')}
                    </p>
                  </div>

                  {/* Temperature range */}
                  <div className="text-right flex-shrink-0">
                    {forecast.temp_min_c !== null && forecast.temp_max_c !== null ? (
                      <p className="font-sans text-base font-bold text-white tabular-nums">
                        {Math.round(forecast.temp_max_c)}&deg;
                        <span className="text-white/70 font-normal text-xs ml-0.5">
                          / {Math.round(forecast.temp_min_c)}&deg;
                        </span>
                      </p>
                    ) : (
                      <p className="font-sans text-base font-bold text-white">--</p>
                    )}
                  </div>
                </div>

                {/* Precipitation and wind details */}
                <div className="flex items-center gap-3 mt-2">
                  {forecast.precipitation_mm !== null && (
                    <span className="text-xs font-sans text-white/70">
                      {t('weather.precip', 'Precip')}: {forecast.precipitation_mm.toFixed(1)} mm
                    </span>
                  )}
                  {forecast.wind_kph !== null && (
                    <span className="text-xs font-sans text-white/70">
                      {t('weather.wind', 'Wind')}: {Math.round(forecast.wind_kph)} km/h
                    </span>
                  )}
                </div>

                {/* Scenario suggestion */}
                {suggestion && (
                  <div className="flex items-center justify-between mt-2.5 gap-2">
                    <span
                      className="bg-white/20 text-white rounded-md px-2 py-1 text-xs font-sans truncate"
                      title={suggestion.reason}
                    >
                      {suggestion.suggested_condition_type}
                    </span>
                    {onCreateScenario && (
                      <button
                        onClick={() => onCreateScenario(suggestion.suggested_condition_type)}
                        className="flex-shrink-0 text-xs font-sans font-medium text-white hover:bg-white/10 rounded-md px-2 py-1 transition-colors duration-150"
                      >
                        {t('weather.create_scenario', 'Apply')}
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

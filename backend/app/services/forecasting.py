
from pathlib import Path

import numpy as np
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gpm_imerg"
    / "historical_20200101_20200130.zarr"
)

OBSERVATION_INTERVAL_MINUTES = 30
FORECAST_STEPS = 12
EVALUATION_DAYS = 7
STEPS_PER_DAY = 48


def _calculate_metrics(actual, predicted):
    errors = predicted - actual

    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors ** 2))),
        "bias": float(np.mean(errors)),
        "observations": int(len(actual)),
    }


def _evaluate_baselines(series):
    evaluation_steps = EVALUATION_DAYS * STEPS_PER_DAY
    test_start = len(series) - evaluation_steps

    if test_start <= STEPS_PER_DAY:
        raise ValueError("Insufficient historical data for chronological evaluation.")

    actual_values = []
    persistence_predictions = []
    seasonal_predictions = []

    # Each forecast origin produces one independent 6-hour block.
    # No actual values inside a forecast block are used to predict
    # later steps within that same block.
    origin = test_start - 1

    while origin < len(series) - 1:
        block_end = min(origin + FORECAST_STEPS, len(series) - 1)

        for target_index in range(origin + 1, block_end + 1):
            seasonal_index = target_index - STEPS_PER_DAY

            if seasonal_index < 0:
                raise ValueError("Insufficient history for the previous-day baseline.")

            actual_values.append(series[target_index])
            persistence_predictions.append(series[origin])
            seasonal_predictions.append(series[seasonal_index])

        origin = block_end

    actual = np.asarray(actual_values, dtype=float)
    persistence = np.asarray(persistence_predictions, dtype=float)
    seasonal = np.asarray(seasonal_predictions, dtype=float)

    persistence_metrics = _calculate_metrics(actual, persistence)
    seasonal_metrics = _calculate_metrics(actual, seasonal)

    # Select the lower-MAE baseline. Persistence wins an exact tie.
    if seasonal_metrics["mae"] < persistence_metrics["mae"]:
        selected_model = "previous_day"
        selected_metrics = seasonal_metrics
    else:
        selected_model = "persistence"
        selected_metrics = persistence_metrics

    return {
        "evaluation_period": {
            "days": EVALUATION_DAYS,
            "start_index": int(test_start),
            "end_index": int(len(series) - 1),
            "forecast_horizon_steps": FORECAST_STEPS,
            "forecast_horizon_hours": 6,
            "evaluation_method": "chronological_rolling_origin",
        },
        "persistence": persistence_metrics,
        "previous_day": seasonal_metrics,
        "selected_baseline": selected_model,
        "selected_metrics": selected_metrics,
    }


def get_gpm_forecast_data():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Historical dataset not found: {DATASET_PATH}"
        )

    dataset = xr.open_zarr(DATASET_PATH)

    try:
        if "precipitation" not in dataset:
            raise ValueError("Dataset does not contain precipitation.")

        precipitation = dataset["precipitation"]

        expected_dimensions = ("time", "latitude", "longitude")

        if precipitation.dims != expected_dimensions:
            raise ValueError(
                f"Unexpected precipitation dimensions: {precipitation.dims}"
            )

        values = np.asarray(precipitation.values, dtype=float)
        timestamps = np.asarray(dataset["time"].values)

        if values.ndim != 3:
            raise ValueError("Precipitation data must have three dimensions.")

        if values.shape[0] != len(timestamps):
            raise ValueError("Timestamp and precipitation lengths do not match.")

        if len(timestamps) < 384:
            raise ValueError("At least 8 days of observations are required.")

        if not np.isfinite(values).all():
            raise ValueError(
                "Missing or non-finite precipitation values were detected."
            )

        if not np.issubdtype(timestamps.dtype, np.datetime64):
            raise ValueError("Dataset timestamps are not datetime values.")

        time_differences = np.diff(timestamps)

        expected_interval = np.timedelta64(
            OBSERVATION_INTERVAL_MINUTES, "m"
        )

        if not np.all(time_differences == expected_interval):
            raise ValueError(
                "Timestamps are not continuous at 30-minute intervals."
            )

        # Match the Time Series page: average the four grid cells
        # into one regional spatial-mean observation per timestamp.
        series = np.mean(values, axis=(1, 2))

        evaluation = _evaluate_baselines(series)

        selected_model = evaluation["selected_baseline"]

        future_values = []

        for step in range(FORECAST_STEPS):
            if selected_model == "previous_day":
                source_index = len(series) + step - STEPS_PER_DAY
                prediction = series[source_index]
            else:
                prediction = series[-1]

            future_values.append(float(prediction))

        future_timestamps = [
            np.datetime_as_string(
                timestamps[-1] + np.timedelta64(
                    (step + 1) * OBSERVATION_INTERVAL_MINUTES, "m"
                ),
                unit="s",
            )
            for step in range(FORECAST_STEPS)
        ]

        recent_history_steps = min(STEPS_PER_DAY, len(series))

        history_start = len(series) - recent_history_steps

        historical_timestamps = [
            np.datetime_as_string(timestamp, unit="s")
            for timestamp in timestamps[history_start:]
        ]

        historical_values = [
            float(value) for value in series[history_start:]
        ]

        latitude = np.asarray(dataset["latitude"].values, dtype=float)
        longitude = np.asarray(dataset["longitude"].values, dtype=float)

        return {
            "status": "success",
            "source": "NASA GPM IMERG V07B",
            "forecast_type": "four_cell_regional_spatial_mean",
            "variable": "precipitation",
            "units": precipitation.attrs.get("units", "mm/hr"),
            "observation_interval_minutes": OBSERVATION_INTERVAL_MINUTES,
            "forecast_horizon_hours": 6,
            "forecast_steps": FORECAST_STEPS,
            "historical_observations": int(len(series)),
            "grid_cells": int(values.shape[1] * values.shape[2]),
            "spatial_coverage": {
                "latitude": [float(latitude.min()), float(latitude.max())],
                "longitude": [float(longitude.min()), float(longitude.max())],
            },
            "last_observation_time": np.datetime_as_string(
                timestamps[-1], unit="s"
            ),
            "evaluation": evaluation,
            "forecast": {
                "selected_baseline": selected_model,
                "timestamps": future_timestamps,
                "values": future_values,
            },
            "recent_history": {
                "timestamps": historical_timestamps,
                "values": historical_values,
            },
            "uncertainty": {
                "estimated": False,
                "message": (
                    "Calibrated prediction intervals have not been estimated."
                ),
            },
            "limitations": [
                "Evaluation uses only the final seven days of this 30-day dataset.",
                "The forecast represents the spatial mean of four grid cells.",
                "The selected method is a statistical baseline, not an AI model.",
                "Performance may not generalize beyond this region or period.",
            ],
        }

    finally:
        dataset.close()

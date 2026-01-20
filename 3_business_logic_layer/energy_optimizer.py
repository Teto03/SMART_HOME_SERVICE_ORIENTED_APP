from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from flask import Flask, jsonify, request

app = Flask(__name__)


ALLOWED_SEASON_MODES = {"auto", "summer", "winter", "mild"}


@dataclass
class WindowMetrics:
    count: int
    any_open: bool
    all_open: bool


@dataclass
class SeasonContext:
    current: str
    is_summer: bool
    is_winter: bool
    is_mild: bool


@dataclass
class OptimizationContext:
    indoor_temp: float
    outdoor_temp: float
    window_states: Dict[str, str]
    boiler_status: str
    ac_status: str
    season_mode: str
    humidity: float = 50.0
    @property
    def window_metrics(self) -> WindowMetrics:
        open_count = sum(1 for status in self.window_states.values() if status == "OPEN")
        any_open = open_count > 0
        all_open = bool(self.window_states) and open_count == len(self.window_states)
        return WindowMetrics(open_count, any_open, all_open)


@dataclass
class EvaluationResult:
    message: str
    should_act: bool
    efficiency_score: int

def clamp_score(score: float) -> int:
    return int(max(0, min(10, round(score))))

# Create the context with states of the devices and the season selected
def build_context(data: Dict) -> OptimizationContext:
    indoor_temp = data.get("indoor_temp")
    outdoor_temp = data.get("outdoor_temp")
    window_states = data.get("window_states")
    boiler_status = str(data.get("boiler_status", "UNKNOWN")).upper()
    ac_status = str(data.get("ac_status", "UNKNOWN")).upper()
    season_mode = str(data.get("season_mode", "auto")).lower()
    if season_mode not in ALLOWED_SEASON_MODES:
        season_mode = "auto"
    return OptimizationContext(
        indoor_temp=indoor_temp,
        outdoor_temp=outdoor_temp,
        window_states=window_states,
        boiler_status=boiler_status,
        ac_status=ac_status,
        season_mode=season_mode,
    )


def detect_season(ctx: OptimizationContext) -> SeasonContext:
    if ctx.season_mode == "summer":
        current = "summer"
    elif ctx.season_mode == "winter":
        current = "winter"
    elif ctx.season_mode == "mild":
        current = "mild"
    else: # if the season is in auto, detect it by the outside temperature
        if ctx.outdoor_temp > 25:
            current = "summer"
        elif ctx.outdoor_temp < 15:
            current = "winter"
        else:
            current = "mild"
    return SeasonContext(
        current=current,
        is_summer = current == "summer",
        is_winter = current == "winter",
        is_mild = current == "mild",
    )


def build_critical_checks(ctx: OptimizationContext, season: SeasonContext) -> List[EvaluationResult]:
    results = []
    metrics = ctx.window_metrics
    
    if season.is_summer and ctx.boiler_status == "ON":
        results.append(EvaluationResult(
            message="Heating is ON during Summer!",
            should_act=True,
            efficiency_score=1
        ))
    
    if season.is_winter and ctx.ac_status == "ON":
        results.append(EvaluationResult(
            message="AC is ON during Winter!",
            should_act=True,
            efficiency_score=1
        ))

    if ctx.ac_status == "ON" and ctx.boiler_status == "ON":
        results.append(EvaluationResult(
            message="Heating and Cooling are ON simultaneously!",
            should_act=True,
            efficiency_score=1
        ))

    if ctx.ac_status == "ON" and metrics.any_open:
        window_count_msg = f"({metrics.count} window{'s' if metrics.count > 1 else ''} open)"
        results.append(EvaluationResult(
            message=f"AC is ON while windows are OPEN {window_count_msg}",
            should_act=True,
            efficiency_score=2 if metrics.count == 1 else 1
        ))
    
    if ctx.boiler_status == "ON" and metrics.any_open:
        results.append(EvaluationResult(
            message=f"Boiler is ON with windows OPEN",
            should_act=True,
            efficiency_score=1
        ))

    return results


def evaluate_summer(ctx: OptimizationContext, metrics: WindowMetrics) -> EvaluationResult:
    if ctx.indoor_temp > 26:
        if ctx.ac_status == "ON":
             return EvaluationResult(
                message=f"Cooling in progress. Indoor: {ctx.indoor_temp}°C.",
                should_act=False,
                efficiency_score=7
            )
        
        if metrics.any_open:
            if ctx.outdoor_temp > ctx.indoor_temp:
                 return EvaluationResult(
                     message="It's hotter outside! Close windows to keep heat out.",
                     should_act=True,
                     efficiency_score=4
                 )
            else:
                 return EvaluationResult(
                     message="Natural cooling active (Windows Open). Monitor temperature.",
                     should_act=False,
                     efficiency_score=8
                 )
        else:
             return EvaluationResult(
                 message="Temperature is too high! Turn on AC.",
                 should_act=True,
                 efficiency_score=5
             )

    if ctx.indoor_temp > ctx.outdoor_temp and not (metrics.any_open) and ctx.ac_status == "ON":
        return EvaluationResult(
            message="It's cooler outside! Open windows instead of using AC.",
            should_act=True,
            efficiency_score=6
        )

    if metrics.any_open and ctx.ac_status != "ON":
        return EvaluationResult(
            message=f"Good! Windows are open for natural ventilation in summer.",
            should_act=False,
            efficiency_score=9
        )

    return EvaluationResult(
        message=f"System stable. Summer mode. Indoor: {ctx.indoor_temp}°C, Outdoor: {ctx.outdoor_temp}°C.",
        should_act=False,
        efficiency_score=7
    )


def evaluate_winter(ctx: OptimizationContext, metrics: WindowMetrics) -> EvaluationResult:
    if metrics.any_open:
        return EvaluationResult(
            message="Windows open in cold weather!",
            should_act=True,
            efficiency_score=3
        )
    if ctx.boiler_status == "ON" and ctx.indoor_temp >= 24:
        return EvaluationResult(
            message="High temperature inside! Turn off boiler.",
            should_act=True,
            efficiency_score=2
        )
    return EvaluationResult(
        message=f"System stable. Winter mode. Indoor: {ctx.indoor_temp}°C, Outdoor: {ctx.outdoor_temp}°C.",
        should_act=False,
        efficiency_score=7
    )


def evaluate_mild(ctx: OptimizationContext, metrics: WindowMetrics) -> EvaluationResult:
    if 20.0 <= ctx.indoor_temp <= 22.0:
        if ctx.boiler_status == "ON" or ctx.ac_status == "ON":
            return EvaluationResult(
                message="Temperature is ideal (20-22°C). Turn off heating/cooling to save energy.",
                should_act=True,
                efficiency_score=6
            )
        else:
             return EvaluationResult(
                message="Temperature is ideal (20-22°C). Systems off. Good job!",
                should_act=False,
                efficiency_score=10
            )

    if ctx.indoor_temp > 24 and ctx.outdoor_temp < ctx.indoor_temp - 2:
        if not metrics.any_open:
            return EvaluationResult(
                message="It's cooler outside! Open windows to cool down naturally.",
                should_act=True,
                efficiency_score=6
            )
        if ctx.ac_status == "ON":
             return EvaluationResult(
                message="Natural cooling active. Turn off AC to save energy.",
                should_act=True,
                efficiency_score=5
             )

    if ctx.indoor_temp < 20 and ctx.outdoor_temp > ctx.indoor_temp + 2 and ctx.outdoor_temp < 25:
        if not metrics.any_open:
            return EvaluationResult(
                message="It's warmer outside! Open windows to warm up naturally.",
                should_act=True,
                efficiency_score=6
            )
        if ctx.boiler_status == "ON":
             return EvaluationResult(
                message="Natural heating active. Turn off Boiler to save energy.",
                should_act=True,
                efficiency_score=5
             )

    # Fallback to existing logic for other cases or preserve stability
    if ctx.indoor_temp > ctx.outdoor_temp + 3 and not (metrics.any_open) and ctx.ac_status == "ON":
        return EvaluationResult(
            message=f"It's cool outside! Open windows instead of using AC",
            should_act=True,
            efficiency_score=6
        )
    
    return EvaluationResult(
        message=f"System stable. Mild weather. Indoor: {ctx.indoor_temp}°C, Outdoor: {ctx.outdoor_temp}°C.",
        should_act=False,
        efficiency_score=8
    )


def evaluate_default(ctx: OptimizationContext) -> EvaluationResult:
    return EvaluationResult(
        message=f"System stable. Indoor: {ctx.indoor_temp}°C, Outdoor: {ctx.outdoor_temp}°C.",
        should_act=False,
        efficiency_score=10
    )


def evaluate_seasonal(ctx: OptimizationContext, season: SeasonContext) -> EvaluationResult:
    metrics = ctx.window_metrics
    if season.is_summer:
        return evaluate_summer(ctx, metrics)
    if season.is_winter:
        return evaluate_winter(ctx, metrics)
    if season.is_mild:
        return evaluate_mild(ctx, metrics)
    return evaluate_default(ctx)


def run_evaluation(ctx: OptimizationContext) -> Tuple[EvaluationResult, SeasonContext]:
    season = detect_season(ctx)
    critical_checks = build_critical_checks(ctx, season)
    
    if critical_checks:
        # Combine messages and find worst score
        combined_msg = "<br>".join([res.message for res in critical_checks])
        min_score = min(res.efficiency_score for res in critical_checks)
        result = EvaluationResult(
            message=combined_msg,
            should_act=True,
            efficiency_score=min_score
        )
    else:
        result = evaluate_seasonal(ctx, season)
    
    result.efficiency_score = clamp_score(result.efficiency_score)
    return result, season


@app.route("/optimize_energy", methods=["POST"])
def optimize_energy():
    try:
        ctx = build_context(request.json or {})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    result, season = run_evaluation(ctx)
    return jsonify(
        {
            "message": result.message,
            "should_act": result.should_act,
            "efficiency_score": result.efficiency_score,
            "season": season.current,
            "windows_open_count": ctx.window_metrics.count,
        }
    )


if __name__ == "__main__":
    print("Starting Energy Optimizer on port 5006...")
    app.run(host="0.0.0.0", port=5006, debug=True)

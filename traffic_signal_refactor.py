# traffic_signal_refactor.py
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# -----------------------------
# Tables copied from Chapter 5
# -----------------------------

def vol_cyc_max_green(vol_per_lane: int, cycle_length_s: int) -> int:
    cycle_lengths = [50, 60, 70, 80, 90, 100, 110, 120]
    table = {
        100: [15, 15, 15, 15, 15, 15, 15, 15],
        200: [15, 15, 15, 15, 16, 18, 19, 21],
        300: [15, 16, 19, 21, 24, 26, 29, 31],
        400: [18, 21, 24, 28, 31, 34, 38, 41],
        500: [22, 26, 30, 34, 39, 43, 47, 51],
        600: [26, 31, 36, 41, 46, 51, 56, 61],
        700: [30, 36, 42, 48, 54, 59, 65, 71],
        800: [34, 41, 48, 54, 61, 68, 74, 81],
    }
    if vol_per_lane not in table:
        raise KeyError(f"Phase Volume {vol_per_lane} not in table {sorted(table.keys())}")
    if cycle_length_s not in cycle_lengths:
        raise KeyError(f"Cycle Length {cycle_length_s} not in table {cycle_lengths}")
    col = cycle_lengths.index(cycle_length_s)
    return table[vol_per_lane][col]

_MIN_GAP_COLUMNS = [25, 30, 35, 40, 45]
_MIN_GAP_TABLE: Dict[int, List[float]] = {
    6:  [1.2, 1.3, 1.4, 1.5, 1.6],
    15: [0.9, 1.1, 1.2, 1.3, 1.4],
    25: [0.6, 0.8, 1.0, 1.1, 1.2],
    35: [0.3, 0.6, 0.8, 0.9, 1.1],
    45: [0.0, 0.3, 0.6, 0.7, 0.9],
    55: [0.0, 0.1, 0.3, 0.6, 0.7],
    65: [0.0, 0.0, 0.1, 0.4, 0.5],
    75: [0.0, 0.0, 0.0, 0.2, 0.4],
}

def min_gap_from_table(detect_len_ft: int, v85_mph: int) -> float:
    if detect_len_ft not in _MIN_GAP_TABLE:
        raise KeyError(f"Detection Zone Length {detect_len_ft} not in table {sorted(_MIN_GAP_TABLE.keys())}")
    if v85_mph not in _MIN_GAP_COLUMNS:
        raise KeyError(f"Approach Velocity {v85_mph} not in table {_MIN_GAP_COLUMNS}")
    col = _MIN_GAP_COLUMNS.index(v85_mph)
    return _MIN_GAP_TABLE[detect_len_ft][col]

# -----------------------------
# Change & clearance policy
# -----------------------------

def change_period(t: float, v_mph: float, a: float, g: float, W_ft: float, L_v_ft: float) -> float:
    term1 = t + (1.47 * v_mph) / (2 * (a + 32.2 * g))
    term2 = (W_ft + L_v_ft) / (1.47 * v_mph)
    return term1 + term2

def compute_yellow_and_all_red(v85_mph: float, W_ft: float, g_grade: float,
                               policy: str = 'permissive', t: float = 1.0,
                               a: float = 10.0, L_v: float = 20.0) -> Tuple[float, float]:
    CP = change_period(t=t, v_mph=v85_mph, a=a, g=g_grade, W_ft=W_ft, L_v_ft=L_v)
    yellow_first_term = t + (1.47 * v85_mph) / (2 * (a + 32.2 * g_grade))
    all_red_second_term = CP - yellow_first_term
    if policy == 'restrictive':
        yellow, all_red = CP, 0.0
    else:
        yellow, all_red = yellow_first_term, all_red_second_term
    yellow = max(3.0, min(6.0, yellow))
    all_red = max(0.0, round(all_red, 1))
    return round(yellow, 1), all_red

# -----------------------------
# Pedestrian timing
# -----------------------------

def pedestrian_times(crossing_ft: float, walk_policy: str = 'typical', walk_sec: Optional[int] = None,
                     walk_speed_fps: float = 3.5) -> Tuple[int, float]:
    if walk_sec is None:
        if walk_policy == 'high_peds':
            walk_sec = 10
        elif walk_policy == 'low_peds':
            walk_sec = 7
        else:
            walk_sec = 7
    ped_clear = crossing_ft / walk_speed_fps
    return int(round(walk_sec)), round(ped_clear, 1)

_DEF_GEXPT = {
    "Major Arterial (>40)": 10,
    "Major Arterial (<40)": 7,
    "Minor Arterial": 4,
    "Collector": 2,
}

def driver_expectancy_min_green(facility_type: str, phase_type: str = 'Through') -> int:
    if phase_type == 'Left-Turn':
        return 2
    return _DEF_GEXPT.get(facility_type, 4)


def queue_clearance_min_green(distance_ft: Optional[float]) -> int:
    if distance_ft is None:
        return 0
    d = distance_ft
    if 0 <= d <= 25:
        return 5
    elif d <= 50:
        return 7
    elif d <= 75:
        return 9
    elif d <= 100:
        return 11
    elif d <= 125:
        return 13
    elif d <= 150:
        return 15
    else:
        return 15


def minimum_green(stopline_detect: bool,
                  ped_pushbutton: bool,
                  separate_ped_displays: bool,
                  facility_type: str,
                  crossing_ft: Optional[float],
                  queue_distance_ft: Optional[float],
                  phase_type: str = 'Through') -> float:
    ge = driver_expectancy_min_green(facility_type, phase_type)
    gq = queue_clearance_min_green(queue_distance_ft) if not stopline_detect else 0
    gp = 0
    if (not separate_ped_displays) or (not ped_pushbutton):
        if crossing_ft is None:
            raise ValueError("crossing_ft required for pedestrian timing when ped displays absent or pushbutton absent")
        walk, clear = pedestrian_times(crossing_ft)
        gp = walk + clear
    return max(ge, gq, gp)

# -----------------------------
# Passage time and gap reduction
# -----------------------------

def passage_time_from_MAH(mah_s: float, v85_mph: float, veh_len_ft: float, det_len_ft: float) -> float:
    v_avg_fps = 1.467 * (0.88 * v85_mph)
    return round(mah_s - (veh_len_ft + det_len_ft) / v_avg_fps, 2)


def effective_gap(t_green_s: float, PT_initial: float, min_gap: float,
                  time_before_reduction: float, time_to_reduce: float) -> float:
    if t_green_s <= time_before_reduction:
        return PT_initial
    end = time_before_reduction + max(0.0, time_to_reduce)
    if t_green_s >= end:
        return min_gap
    frac = (t_green_s - time_before_reduction) / max(0.001, time_to_reduce)
    return PT_initial - frac * (PT_initial - min_gap)

# -----------------------------
# Minimal phase state machine
# -----------------------------

@dataclass
class PhaseParams:
    min_green: float
    max_green: float
    PT_initial: float
    min_gap: float
    t_before_reduction: float
    t_to_reduce: float
    yellow: float
    all_red: float


class PhaseSimulator:
    def __init__(self, params: PhaseParams, conflicting_call_present: bool = True):
        self.p = params
        self.conflicting = conflicting_call_present

    def run(self, call_times: List[float]) -> Dict[str, float]:
        call_times = sorted(call_times)
        t = 0.0
        green = 0.0
        i = 0
        last_call_time = 0.0
        while True:
            next_call = call_times[i] if i < len(call_times) else None
            eff_gap = effective_gap(green, self.p.PT_initial, self.p.min_gap,
                                    self.p.t_before_reduction, self.p.t_to_reduce)
            if next_call is None:
                if self.conflicting and green >= max(self.p.min_green, last_call_time + eff_gap):
                    break
                t += 0.1
                green += 0.1
                if green >= self.p.max_green:
                    green = self.p.max_green
                    break
                continue
            if self.conflicting and (next_call - last_call_time) > eff_gap and green >= self.p.min_green:
                green = max(green, last_call_time + eff_gap)
                break
            t = next_call
            green = t
            last_call_time = next_call
            i += 1
            if green >= self.p.max_green:
                green = self.p.max_green
                break
        total_green = min(green, self.p.max_green)
        return {
            'green': round(total_green, 1),
            'yellow': self.p.yellow,
            'all_red': self.p.all_red,
            'change_and_clear': round(total_green + self.p.yellow + self.p.all_red, 1)
        }

# -----------------------------
# Demonstration with synthetic call pattern
# -----------------------------

def demo():
    v85 = 30
    W = 60
    grade = 0.0
    facility = 'Minor Arterial'
    stopline_detect = False
    ped_pushbutton = True
    separate_ped_displays = False
    crossing_ft = 60
    queue_distance_ft = 100

    g_min = minimum_green(stopline_detect, ped_pushbutton, separate_ped_displays,
                          facility, crossing_ft, queue_distance_ft)

    g_max = vol_cyc_max_green(200, 120)

    yellow, all_red = compute_yellow_and_all_red(v85, W, grade, policy='permissive')

    MAH_initial = 4.0
    det_len = 15
    veh_len = 18
    PT_initial = passage_time_from_MAH(MAH_initial, v85, veh_len, det_len)
    min_gap = min_gap_from_table(det_len, v85)

    params = PhaseParams(min_green=g_min, max_green=max(g_max, g_min), PT_initial=PT_initial,
                         min_gap=min_gap, t_before_reduction=5.0, t_to_reduce=10.0,
                         yellow=yellow, all_red=all_red)

    call_times = [0.5, 1.0, 1.6, 2.3, 3.2, 4.2, 5.4, 6.8, 8.5, 10.6, 13.2, 16.5, 20.5]

    sim = PhaseSimulator(params, conflicting_call_present=True)
    result = sim.run(call_times)

    lines = []
    lines.append("DEMO RESULTS (synthetic calls)\n")
    lines.append(f"v85 = {v85} mph, W = {W} ft, grade = {grade}\n")
    lines.append(f"Min Green = {g_min:.1f} s, Max Green = {g_max:.1f} s\n")
    lines.append(f"PT_initial = {PT_initial:.2f} s (MAH=4.0), MinGap = {min_gap:.1f} s (Table 5-11)\n")
    lines.append("Gap Reduction: TBR = 5 s, TTR = 10 s\n")
    lines.append(f"Yellow = {yellow:.1f} s, All-Red = {all_red:.1f} s\n")
    lines.append(f"Simulated Green = {result['green']:.1f} s; Change+Clear total = {result['change_and_clear']:.1f} s\n")
    return "".join(lines)

if __name__ == '__main__':
    print(demo())

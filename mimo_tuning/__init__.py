"""
Industrial Control AI Utils - MIMO Tuning Module

PID tuning methods for SISO and MIMO systems:
- Ziegler-Nichols open-loop method
- Cohen-Coon method
- Lambda tuning
- RGA (Relative Gain Array) for MIMO pairing
- Static decoupler design
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PIDParams:
    """PID controller parameters."""
    Kc: float  # Proportional gain
    Ti: float  # Integral time
    Td: float  # Derivative time
    Ts: float  # Sampling time


@dataclass
class MIMOTuningResult:
    """MIMO tuning result."""
    pairings: List[Tuple[int, int]]
    loop_params: Dict[str, PIDParams]
    rga: np.ndarray
    coupling_score: float
    decoupler: Optional[np.ndarray]


def ziegler_nichols_open_loop(K: float, tau: float, theta: float) -> PIDParams:
    """
    Ziegler-Nichols open-loop tuning method.
    
    Args:
        K: Process gain
        tau: Time constant
        theta: Dead time (transport delay)
    
    Returns:
        PIDParams with Kc, Ti, Td
    """
    if theta <= 0:
        theta = tau * 0.1  # Default: 10% of time constant
    
    Kc = 1.2 * tau / (K * theta)
    Ti = 2.0 * theta
    Td = 0.5 * theta
    
    return PIDParams(Kc=round(Kc, 3), Ti=round(Ti, 3), Td=round(Td, 3), Ts=0.1)


def cohen_coon(K: float, tau: float, theta: float) -> PIDParams:
    """
    Cohen-Coon tuning method.
    
    Args:
        K: Process gain
        tau: Time constant
        theta: Dead time
    
    Returns:
        PIDParams
    """
    if theta <= 0:
        theta = tau * 0.1
    
    tau_ratio = theta / tau if tau > 0 else 0.1
    
    Kc = (1.0 / K) * (tau / theta + 1.0 / 3.0)
    Ti = theta * (30.0 + 3.0 * tau_ratio) / (9.0 + 20.0 * tau_ratio)
    Td = theta * 4.0 / (11.0 + 6.0 * tau_ratio)
    
    return PIDParams(Kc=round(Kc, 3), Ti=round(Ti, 3), Td=round(Td, 3), Ts=0.1)


def lambda_tuning(K: float, tau: float, theta: float, Ts: float = 0.1) -> PIDParams:
    """
    Lambda (internal model control) tuning method.
    
    Args:
        K: Process gain
        tau: Time constant
        theta: Dead time
        Ts: Sampling time
    
    Returns:
        PIDParams
    """
    lambda_tau = max(Ts * 3, theta)
    Kc = tau / (K * (lambda_tau + theta))
    Ti = tau
    Td = 0.0
    
    return PIDParams(Kc=round(Kc, 3), Ti=round(Ti, 3), Td=round(Td, 3), Ts=Ts)


def calculate_rga(gain_matrix: np.ndarray) -> np.ndarray:
    """
    Calculate Relative Gain Array (RGA).
    
    RGA = G * (G^{-1})^T
    
    Diagonal elements close to 1 indicate good pairings.
    
    Args:
        gain_matrix: steady-state gain matrix (n_out x n_in)
    
    Returns:
        RGA matrix
    """
    try:
        G_inv = np.linalg.inv(gain_matrix)
        return gain_matrix * G_inv.T
    except np.linalg.LinAlgError:
        return np.eye(gain_matrix.shape[0])


def suggest_pairings(rga: np.ndarray) -> List[Tuple[int, int]]:
    """
    Suggest input-output pairings based on RGA.
    Greedy algorithm: pair elements closest to 1.
    
    Args:
        rga: Relative Gain Array
    
    Returns:
        List of (input_idx, output_idx) pairs
    """
    n = rga.shape[0]
    pairings = []
    used_out = set()
    used_in = set()
    
    for _ in range(n):
        best_val = -1
        best_pair = (0, 0)
        
        for i in range(n):
            for j in range(n):
                if i not in used_out and j not in used_in:
                    if rga[i, j] > best_val:
                        best_val = rga[i, j]
                        best_pair = (j, i)  # (input, output)
        
        if best_pair[0] not in used_in and best_pair[1] not in used_out:
            pairings.append(best_pair)
            used_in.add(best_pair[0])
            used_out.add(best_pair[1])
    
    return pairings


def design_static_decoupler(gain_matrix: np.ndarray) -> Optional[np.ndarray]:
    """
    Design static decoupler as inverse of gain matrix.
    
    Args:
        gain_matrix: steady-state gain matrix
    
    Returns:
        Decoupler matrix (inverse of G), or None if SISO
    """
    n = gain_matrix.shape[0]
    if n == 1:
        return None
    
    try:
        return np.linalg.inv(gain_matrix)
    except np.linalg.LinAlgError:
        return None


def tune_mimo(inputs: List[str], outputs: List[str],
              gain_matrix: np.ndarray, time_constants: np.ndarray,
              delays: np.ndarray, Ts: float = 0.1,
              method: str = "ziegler-nichols") -> MIMOTuningResult:
    """
    Full MIMO tuning workflow.
    
    Args:
        inputs: input variable names
        outputs: output variable names
        gain_matrix: steady-state gain matrix
        time_constants: time constant matrix
        delays: dead time matrix
        Ts: sampling time
        method: tuning method
    
    Returns:
        MIMOTuningResult
    """
    rga = calculate_rga(gain_matrix)
    pairings = suggest_pairings(rga)
    decoupler = design_static_decoupler(gain_matrix)
    
    # Tune each loop individually
    loop_params = {}
    for i, (inp_idx, out_idx) in enumerate(pairings):
        K = abs(gain_matrix[out_idx, inp_idx])
        tau = time_constants[out_idx, inp_idx]
        theta = delays[out_idx, inp_idx]
        
        if method == "cohen-coon":
            params = cohen_coon(K, tau, theta)
        elif method == "lambda":
            params = lambda_tuning(K, tau, theta, Ts)
        else:
            params = ziegler_nichols_open_loop(K, tau, theta)
        
        loop_params[f"loop_{i+1}"] = params
    
    # Coupling score: how close RGA is to identity
    n = rga.shape[0]
    if n == 1:
        coupling_score = 1.0
    else:
        ideal = np.eye(n)
        diff = np.sum(np.abs(rga - ideal))
        max_diff = n * (n - 1)
        coupling_score = max(0, 1.0 - diff / max_diff)
    
    return MIMOTuningResult(
        pairings=pairings,
        loop_params=loop_params,
        rga=rga,
        coupling_score=round(coupling_score, 3),
        decoupler=decoupler
    )


def demo():
    """Demo MIMO tuning."""
    print("=== MIMO PID Tuning ===\n")
    
    # SISO example
    print("SISO (ZN): K=1.0, tau=5.0, theta=1.0")
    params = ziegler_nichols_open_loop(K=1.0, tau=5.0, theta=1.0)
    print(f"  Kc={params.Kc}, Ti={params.Ti}, Td={params.Td}")
    
    # MIMO example
    print("\nMIMO 2x2:")
    G = np.array([[1.0, 0.3], [0.2, 1.0]])
    T = np.array([[5.0, 3.0], [2.0, 6.0]])
    L = np.array([[1.0, 0.5], [0.8, 1.0]])
    
    result = tune_mimo(["u1", "u2"], ["y1", "y2"], G, T, L)
    
    print(f"  RGA:\n{result.rga}")
    print(f"  Pairings: {result.pairings}")
    print(f"  Coupling: {result.coupling_score}")
    for name, p in result.loop_params.items():
        print(f"  {name}: Kc={p.Kc}, Ti={p.Ti}, Td={p.Td}")


if __name__ == "__main__":
    demo()

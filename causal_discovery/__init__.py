"""
Industrial Control AI Utils - Causal Discovery Module

PC algorithm for causal structure discovery from observational data.
Fisher Z-test for partial correlation independence.
Causal pattern classification (chain/fork/collider).

Reference: Spirtes et al., "Causation, Prediction, and Search"
"""

import numpy as np
from typing import List, Tuple, Optional
from itertools import combinations


class CausalDiscoverer:
    """
    PC Algorithm for causal discovery.
    
    Args:
        alpha: significance level for conditional independence test (default 0.05)
    """
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.causal_graph = None
        self.separating_sets = {}
    
    def discover(self, data: np.ndarray, var_names: List[str] = None) -> dict:
        """
        Run PC algorithm on observational data.
        
        Args:
            data: NxP array (N samples, P variables)
            var_names: variable names (optional)
        
        Returns:
            dict with adjacency list and causal patterns
        """
        n_samples, n_vars = data.shape
        
        if var_names is None:
            var_names = [f"X{i}" for i in range(n_vars)]
        
        # Step 1: Start with complete undirected graph
        adj = np.ones((n_vars, n_vars)) - np.eye(n_vars)
        self.separating_sets = {}
        
        # Step 2: Remove edges based on conditional independence
        for cond_size in range(n_vars - 1):
            for i, j in combinations(range(n_vars), 2):
                if adj[i, j] == 0:
                    continue
                
                # Find neighbors of i (excluding j)
                neighbors_i = [k for k in range(n_vars) if k != j and adj[i, k] == 1]
                
                if len(neighbors_i) < cond_size + 1:
                    continue
                
                # Test all conditioning sets of size cond_size
                for cond_set in combinations(neighbors_i, cond_size + 1):
                    cond_list = list(cond_set)
                    p_value = self._partial_correlation_test(data, i, j, cond_list)
                    
                    if p_value > self.alpha:
                        # Conditionally independent -> remove edge
                        adj[i, j] = 0
                        adj[j, i] = 0
                        self.separating_sets[(i, j)] = cond_list
                        self.separating_sets[(j, i)] = cond_list
                        break
        
        # Step 3: Orient edges (simplified v-structure detection)
        adj = self._orient_edges(adj, n_vars)
        
        # Step 4: Classify causal patterns
        patterns = self._classify_patterns(adj, var_names)
        
        self.causal_graph = {
            "adjacency": adj,
            "var_names": var_names,
            "patterns": patterns,
            "n_edges": int(np.sum(adj > 0) / 2),
            "n_variables": n_vars,
        }
        
        return self.causal_graph
    
    def _partial_correlation_test(self, data: np.ndarray, i: int, j: int, 
                                   cond_set: List[int]) -> float:
        """
        Test if X_i and X_j are conditionally independent given cond_set.
        Uses Fisher Z-transform of partial correlation.
        """
        if len(cond_set) == 0:
            # Simple correlation
            r = np.corrcoef(data[:, i], data[:, j])[0, 1]
        else:
            # Partial correlation via regression
            # Regress X_i on cond_set, get residuals
            X_cond = data[:, cond_set]
            if X_cond.ndim == 1:
                X_cond = X_cond.reshape(-1, 1)
            
            # Add bias
            X_cond = np.column_stack([np.ones(len(data)), X_cond])
            
            try:
                beta_i = np.linalg.lstsq(X_cond, data[:, i], rcond=None)[0]
                beta_j = np.linalg.lstsq(X_cond, data[:, j], rcond=None)[0]
                
                resid_i = data[:, i] - X_cond @ beta_i
                resid_j = data[:, j] - X_cond @ beta_j
                
                if np.std(resid_i) < 1e-10 or np.std(resid_j) < 1e-10:
                    return 0.0  # Perfect prediction -> dependent
                
                r = np.corrcoef(resid_i, resid_j)[0, 1]
            except:
                return 1.0  # Can't compute -> assume independent
        
        # Fisher Z-transform
        r = np.clip(r, -0.9999, 0.9999)
        z = 0.5 * np.log((1 + r) / (1 - r))
        n = len(data)
        se = 1.0 / np.sqrt(n - len(cond_set) - 3)
        z_stat = abs(z) / se
        
        # Approximate p-value using normal distribution
        p_value = 2 * (1 - self._normal_cdf(z_stat))
        return p_value
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate standard normal CDF."""
        return 0.5 * (1 + np.tanh(x * np.sqrt(2 / np.pi) * (1 + 0.044715 * x**2)))
    
    def _orient_edges(self, adj: np.ndarray, n_vars: int) -> np.ndarray:
        """
        Orient v-structures (colliders): X -> Z <- Y when X and Y not adjacent.
        Returns weighted adjacency: 1=undirected, 2=directed.
        """
        oriented = adj.copy()
        
        for z in range(n_vars):
            neighbors = [i for i in range(n_vars) if adj[i, z] > 0]
            for i, j in combinations(neighbors, 2):
                # Check if i and j are NOT adjacent (v-structure condition)
                if adj[i, j] == 0:
                    # i -> z <- j (collider)
                    oriented[i, z] = 2  # directed
                    oriented[j, z] = 2  # directed
        
        return oriented
    
    def _classify_patterns(self, adj: np.ndarray, var_names: List[str]) -> List[dict]:
        """Classify causal patterns in the graph."""
        patterns = []
        n = len(var_names)
        
        for i in range(n):
            parents = [j for j in range(n) if adj[j, i] == 2]
            children = [j for j in range(n) if adj[i, j] == 2]
            undirected = [j for j in range(n) if adj[i, j] == 1 and j > i]
            
            if len(parents) > 0 and len(children) > 0:
                patterns.append({
                    "type": "chain",
                    "structure": f"{var_names[parents[0]]} -> {var_names[i]} -> {var_names[children[0]]}",
                })
            elif len(parents) >= 2:
                patterns.append({
                    "type": "collider",
                    "structure": " + ".join([var_names[p] for p in parents]) + f" -> {var_names[i]}",
                })
            elif len(children) >= 2:
                patterns.append({
                    "type": "fork",
                    "structure": f"{var_names[i]} -> " + " + ".join([var_names[c] for c in children[:2]]),
                })
        
        return patterns


def demo():
    """Demo causal discovery with synthetic data."""
    print("=== PC Algorithm Causal Discovery ===\n")
    
    np.random.seed(42)
    n = 1000
    
    # Generate data: X1 -> X2 -> X3, X1 -> X3
    X1 = np.random.randn(n)
    X2 = 0.8 * X1 + 0.3 * np.random.randn(n)
    X3 = 0.5 * X1 + 0.6 * X2 + 0.3 * np.random.randn(n)
    
    data = np.column_stack([X1, X2, X3])
    
    discoverer = CausalDiscoverer(alpha=0.05)
    result = discoverer.discover(data, var_names=["温度", "压力", "废品率"])
    
    print("变量:", result["var_names"])
    print("边数:", result["n_edges"])
    print("邻接矩阵:\n", result["adjacency"])
    print("\n因果模式:")
    for p in result["patterns"]:
        print("  ", p["type"], ":", p["structure"])


if __name__ == "__main__":
    demo()

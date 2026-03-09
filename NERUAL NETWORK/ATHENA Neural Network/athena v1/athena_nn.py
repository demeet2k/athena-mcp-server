"""
ATHENA NN - EMERGENCE COMPILER NEURAL NETWORK
==============================================
The definitive core implementation synthesizing all learnings:

ARCHITECTURE:
- Hybrid Equation: G = D + Ω (continuous attention + discrete hypotheses)
- Parallel Lens Observation (CORE + MDL + Attention branches)
- True Disagreement via Jensen-Shannon (not broken normalization)
- Energy-weighted Amplitude Collapse
- Preserved Invariants: rank transform, HOG, polar histogram

PRINCIPLES:
- Don't REPLACE what works, ADD new perspectives
- Multiple observers on the same invariant outperform any single view
- Express uncertainty when input is genuinely ambiguous
- Compression-as-prior provides semantic knowledge without CNN

Author: Emergence Compiler Framework
"""

import numpy as np
from scipy import ndimage
from scipy.special import softmax as scipy_softmax

# =============================================================================
# FOUNDATIONAL TRANSFORMS
# =============================================================================

def rank_transform(img):
    """
    Convert intensity to ordinal rank values.
    CRITICAL: This is immune to noise amplitude - the key to adversarial robustness.
    """
    flat = img.flatten()
    ranks = np.zeros_like(flat)
    sorted_idx = np.argsort(flat)
    ranks[sorted_idx] = np.linspace(0, 1, len(flat))
    return ranks.reshape(img.shape)

def compute_gradients(img):
    """Sobel gradient computation"""
    gy = ndimage.sobel(img, axis=0)
    gx = ndimage.sobel(img, axis=1)
    mag = np.sqrt(gx**2 + gy**2)
    angle = np.arctan2(gy, gx)
    return gx, gy, mag, angle

# =============================================================================
# Ω: CONTINUOUS OPERATOR - Soft Attention Field
# =============================================================================

def generate_attention_field(R, strength=0.5, iterations=4):
    """
    Generate soft foreground attention via conservative diffusion.
    Uses rank image as base (noise-immune).
    Strength controls how much diffusion vs preservation.
    """
    # Initialize from rank image with center bias
    y, x = np.ogrid[:28, :28]
    center_weight = np.exp(-((y-13.5)**2 + (x-13.5)**2) / 200)
    
    # Seed: high rank + center = likely foreground
    u = R * 0.7 + center_weight * 0.3
    
    # Border suppression
    u[:2, :] *= 0.3
    u[-2:, :] *= 0.3
    u[:, :2] *= 0.3
    u[:, -2:] *= 0.3
    
    # Light diffusion (preserve structure, smooth noise)
    for _ in range(iterations):
        u_smooth = ndimage.uniform_filter(u, size=3)
        u = (1 - strength) * u + strength * u_smooth
    
    # Normalize to [0, 1]
    u = (u - u.min()) / (u.max() - u.min() + 1e-8)
    return u

# =============================================================================
# D: DISCRETE OPERATOR - Hypothesis Masks
# =============================================================================

def generate_mask_hypotheses(attention, R, thresholds=[0.3, 0.4, 0.5, 0.6, 0.7]):
    """
    Generate binary mask hypotheses from attention field.
    Each threshold produces a different interpretation.
    """
    hypotheses = []
    
    for tau in thresholds:
        # Threshold attention field
        mask = (attention >= tau).astype(np.float32)
        
        # Also threshold rank image and combine
        rank_mask = (R >= tau * 0.8).astype(np.float32)
        mask = np.maximum(mask, rank_mask * 0.5)
        mask = (mask > 0.5).astype(np.float32)
        
        # Morphological cleanup
        if mask.sum() > 10:
            mask = ndimage.binary_opening(mask, structure=np.ones((2,2))).astype(np.float32)
            mask = ndimage.binary_closing(mask, structure=np.ones((2,2))).astype(np.float32)
            
            # Keep largest component
            labeled, num = ndimage.label(mask)
            if num > 0:
                sizes = ndimage.sum(mask, labeled, range(1, num+1))
                largest = np.argmax(sizes) + 1
                mask = (labeled == largest).astype(np.float32)
            
            # Fill small holes
            mask = ndimage.binary_fill_holes(mask).astype(np.float32)
        
        hypotheses.append((tau, mask))
    
    return hypotheses

# =============================================================================
# FEATURE EXTRACTION - The Proven CORE
# =============================================================================

def extract_hog(img, mag, angle, mask=None, cells=7, bins=9):
    """
    HOG features - proven geometric robustness.
    Optional mask weighting for attention-conditioned extraction.
    """
    cell_size = 28 // cells
    hog = np.zeros(cells * cells * bins)
    
    if mask is None:
        mask = np.ones_like(img)
    
    for i in range(cells):
        for j in range(cells):
            y0, y1 = i * cell_size, (i+1) * cell_size
            x0, x1 = j * cell_size, (j+1) * cell_size
            
            cell_mag = mag[y0:y1, x0:x1]
            cell_ang = angle[y0:y1, x0:x1]
            cell_mask = mask[y0:y1, x0:x1]
            
            # Weight by magnitude and mask
            weights = cell_mag * cell_mask
            
            for b in range(bins):
                ang_low = -np.pi + b * (np.pi / bins)
                ang_high = ang_low + np.pi / bins
                bin_mask = ((cell_ang >= ang_low) & (cell_ang < ang_high)) | \
                          ((cell_ang + np.pi >= ang_low) & (cell_ang + np.pi < ang_high))
                hog[i * cells * bins + j * bins + b] = weights[bin_mask].sum()
    
    # L2 normalize
    norm = np.sqrt(np.sum(hog**2) + 1e-8)
    return hog / norm

def extract_polar_histogram(img, mask=None, radial_bins=8, angular_bins=8):
    """
    Polar histogram - rotation invariance via principal axis alignment.
    """
    if mask is None:
        mask = np.ones_like(img)
    
    weighted = img * mask
    total_mass = weighted.sum()
    
    if total_mass < 1e-8:
        return np.zeros(radial_bins * angular_bins)
    
    # Find center of mass
    y_idx, x_idx = np.ogrid[:28, :28]
    cy = (weighted * y_idx).sum() / total_mass
    cx = (weighted * x_idx).sum() / total_mass
    
    # Principal axis from covariance
    dy = y_idx - cy
    dx = x_idx - cx
    cxx = (weighted * dx * dx).sum() / total_mass
    cyy = (weighted * dy * dy).sum() / total_mass
    cxy = (weighted * dx * dy).sum() / total_mass
    
    principal_angle = 0.5 * np.arctan2(2 * cxy, cxx - cyy + 1e-8)
    
    # Compute polar coordinates relative to principal axis
    y, x = np.ogrid[:28, :28]
    r = np.sqrt((y - cy)**2 + (x - cx)**2)
    theta = np.arctan2(y - cy, x - cx) - principal_angle
    
    # Normalize radius
    r_max = r.max() + 1e-8
    r_norm = r / r_max
    
    # Build histogram
    polar = np.zeros(radial_bins * angular_bins)
    for ri in range(radial_bins):
        for ti in range(angular_bins):
            r_low = ri / radial_bins
            r_high = (ri + 1) / radial_bins
            t_low = -np.pi + ti * (2 * np.pi / angular_bins)
            t_high = t_low + 2 * np.pi / angular_bins
            
            r_mask = (r_norm >= r_low) & (r_norm < r_high)
            t_mask = (theta >= t_low) & (theta < t_high)
            
            polar[ri * angular_bins + ti] = weighted[r_mask & t_mask].sum()
    
    # Normalize
    polar_sum = polar.sum() + 1e-8
    return polar / polar_sum

def extract_topology(mask):
    """
    Topological features from binary mask.
    Critical for distinguishing confusion pairs (4/9, 5/6, 6/8).
    """
    features = []
    
    # Multi-threshold Euler characteristics
    for thresh in [0.3, 0.5, 0.7]:
        binary = mask > thresh
        
        # Count components
        labeled, num_comp = ndimage.label(binary)
        
        # Count holes
        filled = ndimage.binary_fill_holes(binary)
        holes = filled.astype(int) - binary.astype(int)
        _, num_holes = ndimage.label(holes)
        
        features.extend([num_comp / 3.0, num_holes / 3.0])
    
    # Mass distribution (upper/lower, left/right)
    total = mask.sum() + 1e-8
    upper = mask[:14, :].sum() / total
    left = mask[:, :14].sum() / total
    
    features.extend([upper, 1-upper, left, 1-left])
    
    # Centroid
    if mask.sum() > 0:
        cy, cx = ndimage.center_of_mass(mask)
        features.extend([cy/28.0, cx/28.0])
    else:
        features.extend([0.5, 0.5])
    
    return np.array(features)

def extract_structural(img, mask=None):
    """Additional structural features"""
    if mask is None:
        mask = np.ones_like(img)
    
    features = []
    
    # Quadrant energies
    for qi in range(2):
        for qj in range(2):
            quad = img[qi*14:(qi+1)*14, qj*14:(qj+1)*14]
            quad_mask = mask[qi*14:(qi+1)*14, qj*14:(qj+1)*14]
            features.append((quad * quad_mask).sum())
    
    # Edge density
    _, _, mag, _ = compute_gradients(img)
    edge_density = (mag * mask).sum() / (mask.sum() + 1e-8)
    features.append(edge_density)
    
    # Compactness
    if mask.sum() > 0:
        dilated = ndimage.binary_dilation(mask, iterations=2)
        compactness = mask.sum() / (dilated.sum() + 1e-8)
    else:
        compactness = 0
    features.append(compactness)
    
    return np.array(features)

# =============================================================================
# MDL COMPRESSION PRIOR
# =============================================================================

class CompressionPrior:
    """
    Minimum Description Length prior - provides semantic knowledge.
    "How well does this image compress as digit d?"
    """
    
    def __init__(self, pca_rank=8):
        self.pca_rank = pca_rank
        self.templates = {}  # Per-digit mean
        self.bases = {}      # Per-digit PCA basis
        self.trained = False
    
    def train(self, X_flat, Y):
        """Train compression models per digit"""
        for d in range(10):
            mask = Y.argmax(1) == d
            if mask.sum() < self.pca_rank + 2:
                continue
            
            X_d = X_flat[mask]
            self.templates[d] = X_d.mean(0)
            
            # PCA via SVD
            centered = X_d - self.templates[d]
            try:
                U, S, Vt = np.linalg.svd(centered, full_matrices=False)
                self.bases[d] = Vt[:self.pca_rank].T
            except:
                self.bases[d] = np.eye(784, self.pca_rank)
        
        self.trained = True
    
    def compute_code_lengths(self, x_flat):
        """Compute description length for each digit hypothesis"""
        if not self.trained:
            return np.zeros(10)
        
        lengths = np.zeros(10)
        
        for d in range(10):
            if d not in self.templates:
                lengths[d] = 1000  # Very long = bad fit
                continue
            
            # Project onto digit subspace
            centered = x_flat - self.templates[d]
            coeffs = self.bases[d].T @ centered
            reconstruction = self.templates[d] + self.bases[d] @ coeffs
            
            # Residual = exceptions
            residual = x_flat - reconstruction
            
            # MDL components
            coeff_cost = np.sum(np.abs(coeffs)) * 0.1
            exception_cost = np.sum(np.abs(residual) > 0.15) * 0.5
            residual_cost = np.sum(np.abs(residual)) * 0.2
            
            lengths[d] = coeff_cost + exception_cost + residual_cost
        
        return lengths
    
    def get_logits(self, x_flat):
        """Convert code lengths to logits (shorter = higher logit)"""
        lengths = self.compute_code_lengths(x_flat)
        # Negative because shorter length = better
        return -lengths

# =============================================================================
# BRANCH DISAGREEMENT (Jensen-Shannon)
# =============================================================================

def compute_disagreement(prob_distributions):
    """
    Jensen-Shannon divergence between probability distributions.
    Replaces the broken "agreement = 1.0 always" metric.
    """
    probs = [np.clip(p, 1e-10, 1-1e-10) for p in prob_distributions]
    probs = [p / p.sum() for p in probs]  # Ensure normalized
    
    # Mixture distribution
    m = np.mean(probs, axis=0)
    
    # JS = average KL to mixture
    js = 0
    for p in probs:
        kl = np.sum(p * np.log(p / m))
        js += kl / len(probs)
    
    return js

# =============================================================================
# NEURAL NETWORK CLASSIFIER
# =============================================================================

class NeuralClassifier:
    """Simple but effective MLP classifier"""
    
    def __init__(self, input_dim, hidden1=128, hidden2=64, seed=42):
        rng = np.random.RandomState(seed)
        
        # Xavier initialization
        self.W1 = rng.randn(input_dim, hidden1) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden1)
        self.W2 = rng.randn(hidden1, hidden2) * np.sqrt(2.0 / hidden1)
        self.b2 = np.zeros(hidden2)
        self.W3 = rng.randn(hidden2, 10) * np.sqrt(2.0 / hidden2)
        self.b3 = np.zeros(10)
    
    def forward(self, X):
        """Forward pass with ReLU activations"""
        self.h1 = np.maximum(0, X @ self.W1 + self.b1)
        self.h2 = np.maximum(0, self.h1 @ self.W2 + self.b2)
        logits = self.h2 @ self.W3 + self.b3
        
        # Stable softmax
        logits_stable = logits - logits.max(axis=-1, keepdims=True)
        exp_logits = np.exp(logits_stable)
        self.probs = exp_logits / exp_logits.sum(axis=-1, keepdims=True)
        
        return self.probs
    
    def backward(self, X, Y, lr=0.01, wd=0.001):
        """Backward pass with L2 regularization"""
        batch_size = len(X)
        
        # Output gradient
        dlogits = (self.probs - Y) / batch_size
        
        # Layer 3
        dW3 = self.h2.T @ dlogits + wd * self.W3
        db3 = dlogits.sum(0)
        dh2 = dlogits @ self.W3.T
        dh2[self.h2 <= 0] = 0
        
        # Layer 2
        dW2 = self.h1.T @ dh2 + wd * self.W2
        db2 = dh2.sum(0)
        dh1 = dh2 @ self.W2.T
        dh1[self.h1 <= 0] = 0
        
        # Layer 1
        dW1 = X.T @ dh1 + wd * self.W1
        db1 = dh1.sum(0)
        
        # Update
        self.W3 -= lr * dW3
        self.b3 -= lr * db3
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
    
    def predict(self, X):
        probs = self.forward(X)
        return probs.argmax(axis=-1)

# =============================================================================
# ATHENA NN - MAIN CLASS
# =============================================================================

class AthenaNN:
    """
    ATHENA Neural Network - Emergence Compiler Architecture
    
    Combines:
    - Proven invariant features (HOG, polar, topology)
    - Attention-based foreground separation
    - MDL compression prior for semantic knowledge
    - Multi-hypothesis inference with amplitude collapse
    - True branch disagreement measurement
    """
    
    def __init__(self):
        # Feature dimensions
        self.hog_dim = 441      # 7×7×9
        self.polar_dim = 64     # 8×8
        self.topo_dim = 12      # Multi-threshold topology
        self.struct_dim = 6     # Quadrants + edge + compactness
        
        self.total_dim = self.hog_dim + self.polar_dim + self.topo_dim + self.struct_dim
        
        # Components
        self.classifier = NeuralClassifier(self.total_dim, hidden1=128, hidden2=64)
        self.mdl_prior = CompressionPrior(pca_rank=8)
        
        # Normalization stats
        self.feat_mean = None
        self.feat_std = None
        
        # Hypothesis thresholds (reduced for speed)
        self.thresholds = [0.4, 0.55]
    
    def extract_features(self, img, mask=None):
        """Extract all features for one image"""
        R = rank_transform(img)
        _, _, mag, angle = compute_gradients(R)
        
        if mask is None:
            # Default: use rank-based soft mask
            mask = (R > 0.3).astype(np.float32)
        
        # Core features
        hog = extract_hog(R, mag, angle, mask)
        polar = extract_polar_histogram(R, mask)
        topo = extract_topology(mask)
        struct = extract_structural(R, mask)
        
        return np.concatenate([hog, polar, topo, struct])
    
    def forward(self, img):
        """
        Full forward pass with hypothesis evaluation.
        Returns: predicted class, probability distribution, confidence
        """
        R = rank_transform(img)
        
        # Generate attention field (fast mode)
        attention = generate_attention_field(R, strength=0.3, iterations=2)
        
        # Generate hypotheses
        hypotheses = generate_mask_hypotheses(attention, R, self.thresholds)
        
        # Evaluate each hypothesis
        results = []
        for tau, mask in hypotheses:
            if mask.sum() < 15:
                continue
            
            # Extract features with this mask
            feats = self.extract_features(img, mask)
            
            # Normalize
            if self.feat_mean is not None:
                feats_norm = (feats - self.feat_mean) / (self.feat_std + 1e-8)
            else:
                feats_norm = feats
            
            # Get classifier probabilities
            classifier_probs = self.classifier.forward(feats_norm.reshape(1, -1))[0]
            
            # Get MDL prior probabilities
            mdl_logits = self.mdl_prior.get_logits(img.flatten())
            mdl_probs = scipy_softmax(mdl_logits * 0.5)  # Temperature scaling
            
            # Fused probability (geometric mean / product of experts)
            fused = classifier_probs * mdl_probs
            fused = fused / (fused.sum() + 1e-10)
            
            # Compute disagreement
            disagreement = compute_disagreement([classifier_probs, mdl_probs])
            
            # Mask quality score
            edge_agreement = self._compute_edge_agreement(R, mask)
            
            results.append({
                'tau': tau,
                'mask': mask,
                'classifier_probs': classifier_probs,
                'mdl_probs': mdl_probs,
                'fused_probs': fused,
                'disagreement': disagreement,
                'edge_agreement': edge_agreement,
                'features': feats_norm
            })
        
        if len(results) == 0:
            # Fallback: use raw features
            feats = self.extract_features(img)
            if self.feat_mean is not None:
                feats_norm = (feats - self.feat_mean) / (self.feat_std + 1e-8)
            else:
                feats_norm = feats
            probs = self.classifier.forward(feats_norm.reshape(1, -1))[0]
            return probs.argmax(), probs, 0.5
        
        # Amplitude collapse
        return self._collapse(results)
    
    def _compute_edge_agreement(self, R, mask):
        """How well does mask align with strong edges?"""
        _, _, mag, _ = compute_gradients(R)
        strong_edges = mag > np.percentile(mag, 70)
        
        edge_in_mask = (strong_edges & (mask > 0.5)).sum()
        total_edges = strong_edges.sum() + 1e-8
        
        return edge_in_mask / total_edges
    
    def _collapse(self, results):
        """Energy-weighted amplitude collapse across hypotheses"""
        # Compute energy for each hypothesis (lower = better)
        energies = []
        for r in results:
            confidence = r['fused_probs'].max()
            
            E = -np.log(confidence + 1e-10) \
                + 1.0 * r['disagreement'] \
                - 0.5 * r['edge_agreement']
            
            energies.append(E)
        
        # Convert to amplitudes
        energies = np.array(energies)
        amplitudes = scipy_softmax(-energies * 2.0)  # Temperature
        
        # Weighted combination
        final_probs = np.zeros(10)
        for amp, r in zip(amplitudes, results):
            final_probs += amp * r['fused_probs']
        
        # Normalize
        final_probs = final_probs / (final_probs.sum() + 1e-10)
        
        # Confidence based on winner amplitude and probability
        confidence = amplitudes.max() * final_probs.max()
        
        return final_probs.argmax(), final_probs, confidence
    
    def train(self, X_train, Y_train, epochs=30, lr=0.03, batch_size=32, verbose=True):
        """Train the network"""
        n = len(X_train)
        rng = np.random.RandomState(42)
        
        # Train MDL prior
        if verbose:
            print("  Training compression prior...")
        self.mdl_prior.train(X_train, Y_train)
        
        # Collect features for normalization
        if verbose:
            print("  Computing normalization statistics...")
        
        sample_idx = rng.choice(n, min(200, n), replace=False)
        all_feats = []
        for i in sample_idx:
            img = X_train[i].reshape(28, 28)
            feats = self.extract_features(img)
            all_feats.append(feats)
        
        all_feats = np.array(all_feats)
        self.feat_mean = all_feats.mean(0)
        self.feat_std = all_feats.std(0) + 1e-8
        
        # Training loop
        if verbose:
            print("  Training classifier...")
        
        best_loss = float('inf')
        
        for ep in range(epochs):
            idx = rng.permutation(n)
            epoch_loss = 0
            n_batches = 0
            
            for start in range(0, n, batch_size):
                batch_idx = idx[start:start+batch_size]
                
                # Extract features
                batch_feats = []
                batch_y = []
                for i in batch_idx:
                    img = X_train[i].reshape(28, 28)
                    feats = self.extract_features(img)
                    feats_norm = (feats - self.feat_mean) / self.feat_std
                    batch_feats.append(feats_norm)
                    batch_y.append(Y_train[i])
                
                batch_feats = np.array(batch_feats)
                batch_y = np.array(batch_y)
                
                # Forward + backward
                probs = self.classifier.forward(batch_feats)
                loss = -np.sum(batch_y * np.log(probs + 1e-10)) / len(batch_y)
                epoch_loss += loss
                n_batches += 1
                
                self.classifier.backward(batch_feats, batch_y, lr=lr, wd=0.003)
            
            avg_loss = epoch_loss / n_batches
            if avg_loss < best_loss:
                best_loss = avg_loss
            
            if verbose and (ep + 1) % 10 == 0:
                print(f"    Epoch {ep+1}: loss={avg_loss:.4f}")
    
    def evaluate(self, X_test, Y_test, verbose=True):
        """Evaluate on test set"""
        correct = 0
        total = len(X_test)
        confidences = []
        
        for i in range(total):
            img = X_test[i].reshape(28, 28)
            pred, probs, conf = self.forward(img)
            true_label = Y_test[i].argmax()
            
            if pred == true_label:
                correct += 1
            confidences.append(conf)
        
        accuracy = correct / total
        mean_conf = np.mean(confidences)
        
        if verbose:
            print(f"  Accuracy: {accuracy*100:.1f}%")
            print(f"  Mean confidence: {mean_conf:.3f}")
        
        return accuracy, mean_conf

# =============================================================================
# DATA GENERATION
# =============================================================================

def draw_digit(d):
    """Draw synthetic digit template"""
    img = np.zeros((28, 28), dtype=np.float32)
    
    def line(y0, x0, y1, x1):
        n = max(abs(y1-y0), abs(x1-x0), 1)
        for i in range(n+1):
            y = int(y0 + (y1-y0)*i/n)
            x = int(x0 + (x1-x0)*i/n)
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0,y-1):min(28,y+2), max(0,x-1):min(28,x+2)] = 1.0
    
    def circle(cy, cx, r):
        for angle in np.linspace(0, 2*np.pi, int(2*np.pi*r*2)):
            y, x = int(cy + r*np.sin(angle)), int(cx + r*np.cos(angle))
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0,y-1):min(28,y+2), max(0,x-1):min(28,x+2)] = 1.0
    
    if d == 0: circle(14, 14, 8)
    elif d == 1: line(6, 14, 22, 14)
    elif d == 2:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 14, 10)
        for i in range(8): img[14, 10+i] = 1.0
        line(14, 10, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 3:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 14, 14)
        for i in range(5): img[14, 12+i] = 1.0
        line(14, 14, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 4:
        line(6, 10, 14, 10)
        line(14, 10, 14, 18)
        line(6, 18, 22, 18)
    elif d == 5:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 10, 14, 10)
        for i in range(8): img[14, 10+i] = 1.0
        line(14, 17, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 6:
        circle(16, 14, 6)
        line(6, 10, 16, 10)
    elif d == 7:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 22, 12)
    elif d == 8:
        circle(10, 14, 4)
        circle(18, 14, 4)
    elif d == 9:
        circle(10, 14, 5)
        line(10, 19, 22, 19)
    
    img = ndimage.gaussian_filter(img, 0.8)
    return img / (img.max() + 1e-8)

# Augmentation functions
def aug_geometric(img, rng):
    """Rotation and scale"""
    angle = rng.uniform(-25, 25)
    scale = rng.uniform(0.9, 1.1)
    
    img = ndimage.rotate(img, angle, reshape=False, mode='constant')
    img = ndimage.zoom(img, scale, mode='constant')
    
    # Ensure 28x28
    h, w = img.shape
    if h > 28:
        s = (h - 28) // 2
        img = img[s:s+28, s:s+28]
    elif h < 28:
        pad = (28 - h) // 2
        img = np.pad(img, ((pad, 28-h-pad), (pad, 28-w-pad)), mode='constant')
    
    return np.clip(img[:28, :28], 0, 1)

def aug_adversarial(img, rng):
    """Additive noise"""
    noise = rng.randn(*img.shape) * 0.25
    return np.clip(img + noise, 0, 1)

def aug_cluttered(img, rng):
    """Random distractors"""
    out = img.copy()
    for _ in range(rng.randint(3, 7)):
        y, x = rng.randint(0, 24), rng.randint(0, 24)
        s = rng.randint(2, 4)
        out[y:y+s, x:x+s] = rng.uniform(0.1, 0.3)
    return out

def aug_camouflage(img, rng):
    """Textured background with low contrast"""
    freq = rng.uniform(0.3, 0.6)
    phase = rng.uniform(0, 2*np.pi)
    
    y, x = np.ogrid[:28, :28]
    texture = 0.5 + 0.25 * np.sin(freq * x + phase) * np.cos(freq * y + phase * 0.7)
    texture += rng.randn(28, 28) * 0.08
    
    contrast = rng.uniform(0.15, 0.28)
    fg = texture + contrast
    bg = texture
    
    mask = img > 0.3
    out = np.where(mask, fg, bg)
    return np.clip(out, 0, 1)

def generate_data(n, aug_fn, seed):
    """Generate training/test data"""
    rng = np.random.RandomState(seed)
    X = np.zeros((n, 784), dtype=np.float32)
    Y = np.zeros((n, 10), dtype=np.float32)
    
    for i in range(n):
        d = rng.randint(0, 10)
        X[i] = aug_fn(draw_digit(d), rng).flatten()
        Y[i, d] = 1
    
    return X, Y

# =============================================================================
# BENCHMARK
# =============================================================================

def run_benchmarks():
    """Run full benchmark suite"""
    print("="*80)
    print(" ATHENA NN - EMERGENCE COMPILER NEURAL NETWORK ".center(80))
    print("="*80)
    
    benchmarks = [
        ('GEOMETRIC', aug_geometric),
        ('ADVERSARIAL', aug_adversarial),
        ('CLUTTERED', aug_cluttered),
        ('CAMOUFLAGE', aug_camouflage),
    ]
    
    results = {}
    
    for name, aug_fn in benchmarks:
        print(f"\n{'='*60}")
        print(f" {name} BENCHMARK ".center(60))
        print(f"{'='*60}")
        
        # Generate data
        print("  Generating data...")
        X_train, Y_train = generate_data(600, aug_fn, 100)
        X_test, Y_test = generate_data(150, aug_fn, 200)
        
        # Create and train model
        print("  Creating Athena NN...")
        model = AthenaNN()
        model.train(X_train, Y_train, epochs=20, lr=0.03, verbose=True)
        
        # Evaluate
        print("  Evaluating...")
        acc, conf = model.evaluate(X_test, Y_test, verbose=True)
        results[name] = acc
    
    # Summary
    print("\n" + "="*80)
    print(" FINAL RESULTS ".center(80))
    print("="*80)
    
    print(f"\n{'Benchmark':<15} {'Athena NN':>12} {'v76.1':>12} {'Delta':>12}")
    print("-"*55)
    
    v76_baseline = {
        'GEOMETRIC': 0.948,
        'ADVERSARIAL': 0.934,
        'CLUTTERED': 1.000,
        'CAMOUFLAGE': 0.798
    }
    
    for name in ['GEOMETRIC', 'ADVERSARIAL', 'CLUTTERED', 'CAMOUFLAGE']:
        athena = results[name]
        v76 = v76_baseline[name]
        delta = athena - v76
        print(f"{name:<15} {athena*100:>11.1f}% {v76*100:>11.1f}% {delta*100:>+11.1f}%")
    
    avg_athena = np.mean(list(results.values()))
    avg_v76 = np.mean(list(v76_baseline.values()))
    print("-"*55)
    print(f"{'AVERAGE':<15} {avg_athena*100:>11.1f}% {avg_v76*100:>11.1f}% {(avg_athena-avg_v76)*100:>+11.1f}%")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    results = run_benchmarks()

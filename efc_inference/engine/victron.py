"""
Victron charge engine — CC->CV knee location in battery charge time series.

A regime-bound engine in the spirit of the H2O phase engine: it does not
model the whole battery, only the charge-regime transition. Given a
charge history (voltage and current vs time), it classifies each sample
as CC (constant current, 0) or CV (constant voltage, 1) and locates the
knee where the regime changes.

Physics (declared, minimal):
  CC phase: current is held constant, voltage rises toward the charge
            limit. dI/dt ~ 0.
  CV phase: voltage is held at the limit, current decays. dI/dt < 0 and
            V ~ V_max.

The knee is the first sample where the current has started decaying
(|dI/dt| above threshold) while the voltage is within `v_knee_tol` of
its maximum — the crossing of the regime boundary.

Resolution contract (measured against live VRM 15-minute averages,
2026-09-16): the CC->CV knee lasts minutes-to-hours and is NOT visible
in 15-minute means — averaging flattens the current decay below any
sensible threshold. On coarse data the engine therefore reports
`found=False` instead of guessing; it still classifies charge vs
no-charge phases correctly. Fine-grained series (second-to-minute
resolution) are required for a real knee.

Source contract (same measurement): CC means CONSTANT current. The knee
candidate requires a flat current plateau before the decay — otherwise
a solar-driven charge (variable source power, soft peak) would fake a
CC->CV transition at the solar apex. With a variable source the engine
reports `found=False`: the measurable transition there is the source
power, not the charge protocol. The engine is therefore declared valid
for constant-current sources (grid charging), not for direct
solar-driven charging with variable power.

Data contract: the engine takes time series INJECTED via params — it
never reads live data or any site configuration. (Live VRM history is a
Hetzner-side data source; see step 6/8 notes.)

Engine contract (EFCEngine):
  compute(params, coordinates) -> np.ndarray of regime labels (0/1),
  same length as coordinates.
"""
from __future__ import annotations

import numpy as np

from efc_inference.engine.base_engine import EFCEngine


class VictronChargeEngine(EFCEngine):
    #: Bound to a private, instrumented installation — the node
    #: is kept out of GitHub Pages (rule 16).
    SYNLIGHET = "intern"
    """Locate the CC->CV charge-regime knee in a V/I time series."""

    REQUIRED_PARAMS = ["v_knee_tol", "di_threshold", "cc_flat_threshold"]

    @property
    def name(self) -> str:
        return "victron_cccv"

    # ------------------------------------------------------------------
    # Engine contract
    # ------------------------------------------------------------------
    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Classify each sample: 0 = CC (constant current), 1 = CV.

        params_dict: {v_series, i_series, v_knee_tol, di_threshold,
        cc_flat_threshold}. coordinates: times (np.ndarray, length n).
        Returns: np.ndarray of int labels, length n. Invalid input ->
        all zeros (no transition is claimed).
        """
        t = np.asarray(coordinates, dtype=float)
        n = t.size
        out = np.zeros(n, dtype=int)

        # Closed handling: None params, non-finite/non-positive
        # thresholds, or unordered/non-finite times give no transition.
        if not isinstance(params_dict, dict):
            return out
        if t.ndim != 1 or not np.all(np.isfinite(t)):
            return out
        if n < 2 or np.any(np.diff(t) <= 0):
            return out
        v = np.asarray(params_dict.get("v_series", []), dtype=float)
        i = np.asarray(params_dict.get("i_series", []), dtype=float)
        tol = float(params_dict.get("v_knee_tol", np.nan))
        di_thr = float(params_dict.get("di_threshold", np.nan))
        flat_thr = float(params_dict.get("cc_flat_threshold", np.nan))
        for thr in (tol, di_thr, flat_thr):
            if not (np.isfinite(thr) and thr >= 0):
                return out
        min_cc = 5  # the CC plateau is required over at least 5 bins before the knee
        cv_win, cv_need = 3, 2  # confirmation window AFTER the candidate

        if v.size != n or i.size != n or n < min_cc + cv_win + 1:
            return out
        if not np.all(np.isfinite(v)) or not np.all(np.isfinite(i)):
            return out

        # Smooth the current with a short running mean (window 3) so
        # sensor jitter does not fake a decay.
        pad = np.concatenate(([i[0]], i, [i[-1]]))
        i_s = np.convolve(pad, np.ones(3) / 3.0, mode="valid")

        # dI/dt via central differences divided by the ACTUAL dt (the
        # threshold is per time unit, not per sample) — the same curve gives
        # the same knee regardless of the sampling interval.
        di = np.zeros(n)
        dt_mid = t[2:] - t[:-2]
        di[1:-1] = (i_s[2:] - i_s[:-2]) / dt_mid

        v_max = np.max(v)
        labels = np.zeros(n, dtype=int)
        knee_idx = None
        for k in range(min_cc, n - cv_win):
            # The CC phase: the current must have been FLAT (median |dI/dt|
            # below flat_thr) over the preceding min_cc bins — otherwise the
            # decay is source power (a solar curve), not the CV start.
            plateau = np.median(np.abs(di[k - min_cc:k])) < flat_thr
            decaying = di[k] < -di_thr
            near_limit = v[k] >= v_max - tol
            if not (plateau and decaying and near_limit):
                continue
            # Confirmation window: the transition must HOLD — at least
            # cv_need of the next cv_win bins still decay and the voltage
            # stays near the limit. A one-off spike or a rebound
            # (a solar peak) is not confirmed, and the search continues.
            window = range(k + 1, k + 1 + cv_win)
            dec = sum(1 for j in window
                      if di[j] < -di_thr and v[j] >= v_max - tol)
            if dec >= cv_need:
                knee_idx = k
                break
        if knee_idx is not None:
            labels[knee_idx:] = 1
        return labels

    # ------------------------------------------------------------------
    # Knee location
    # ------------------------------------------------------------------
    def find_knee(self, params_dict: dict, coordinates: np.ndarray) -> dict:
        """Locate the CC->CV knee.

        Returns dict with: found (bool), t_knee, v_knee, i_knee
        (float, NaN when not found), plus n_samples and regime_counts.
        """
        labels = self.compute(params_dict, coordinates)
        t = np.asarray(coordinates, dtype=float)
        v = np.asarray(params_dict.get("v_series", []), dtype=float)
        i = np.asarray(params_dict.get("i_series", []), dtype=float)
        nan = float("nan")
        out = {
            "found": False,
            "t_knee": nan,
            "v_knee": nan,
            "i_knee": nan,
            "n_samples": int(labels.size),
            "n_cc": int(np.sum(labels == 0)),
            "n_cv": int(np.sum(labels == 1)),
        }
        ones = np.flatnonzero(labels == 1)
        if ones.size == 0:
            return out
        k = int(ones[0])
        out.update({
            "found": True,
            "t_knee": float(t[k]) if t.size == labels.size else nan,
            "v_knee": float(v[k]) if v.size == labels.size else nan,
            "i_knee": float(i[k]) if i.size == labels.size else nan,
        })
        return out

    # ------------------------------------------------------------------
    # regime_node() bridge (step 4 pattern): the engine describes
    # itself as a RegimeNode instance. Validity numbers derived from
    # the effective parameters — never hard-coded.
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        tol = float(params_dict.get("v_knee_tol", np.inf))
        di_thr = float(params_dict.get("di_threshold", np.inf))
        validity = (
            "The CC->CV knee: the first instant at which the current falls "
            f"(dI/dt < -{di_thr}) while the voltage is within "
            f"{tol} of its maximum — read as the phase boundary of the "
            "charge regime"
        )
        return {
            "id": "efc.victron_cccv_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the battery's charge/drain thresholds — installation-specific — operating limits"],
            "motor": "victron"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["elektrisk_potensial", "energi", "tid"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The
            # field must still stand here because RegimeNode requires it — the
            # test binds them.
            "nivaa": {
                "indeks": 2,
                "forelder": "batteri.lading",
                "tidsskala": "s",
                "lengdeskala": "installation"
            },            "regime": {
                "name": "Victron charge engine — the CC/CV knee",
                "validity": validity,
                "law_form": (
                    "CC: I constant, V rising. CV: V constant, I "
                    "falling. The knee is read as the transition — analogy "
                    "(not identity) to H2O's triple point."
                ),
            },
            "phase": "regime_engine",
            "measure": {
                "target": "the charge curve V(t), I(t)",
                "measurer": "VictronChargeEngine (injectable time series)",
                "instrument": "V/I time series — the engine never reads live data itself",
                "proxy_chain": [
                    "V(t), I(t) -> regime-labels (0=CC, 1=CV)",
                    "first CV label -> the knee (t_k, V_k, I_k)",
                ],
                "placement": "the engine classifies the regime along time — the same pattern as WaterPhaseEngine in P-T space",
                "compression": "hundreds of V/I measurements -> one knee point",
            },
            "episenter": "the knee frame: CC->CV is read as the phase transition of the charge regime — the triple-point analogy in electrical form",
            "buffer": {
                "role": "the battery's electrochemistry is the buffer that makes the transition possible — the CV phase is interpreted as the buffer's saturation",
                "note": "the engine measures the transition; the buffer is what saturates.",
            },
            "ontology": {
                "assumes": [
                    "CC/CV protocol is the canonical charge protocol",
                    "the knee is readable in V and I alone (no SOC required)",
                ],
                "source": ("CC/CV charge protocol; engine contract "
                           "efc_inference/engine/base_engine.py"),
            },
            "observer": {
                "bandwidth": "the engine sees only V and I — two channels; SOC is not required for the knee",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "CC -> knee -> CV -> saturation — the charge loop's three-stage emergence",
                "properties": ["t_knee", "v_knee", "i_knee"],
            },
            "fractal": {
                "pattern": "the knee is the same transition pattern as the triple point of H2O and L1->L2 — three domains, one pattern (analogy, not identity: charge and phase are not the same quantity)",
                "note": "the engine is the transition's own measurer.",
            },
            "coupling": {
                "local": "the engine works locally on one charge curve at a time",
                "global": "the engine's knee is coupled to the battery.charging node in the atlas (CARRIES) — the measurement carries the regime's transition",
                "empathy_note": "the engine knows which atlas node it carries — the bridge is tested mechanically.",
            },
        }

    # ------------------------------------------------------------------
    # Parameter contract
    # ------------------------------------------------------------------
    def validate_params(self, params_dict: dict) -> bool:
        if not super().validate_params(params_dict):
            return False
        v = np.asarray(params_dict.get("v_series", []), dtype=float)
        i = np.asarray(params_dict.get("i_series", []), dtype=float)
        return v.size >= 3 and i.size == v.size

import { z } from "zod";
export const REGRESSION_EXIT_CODES = {
    WITHIN_POLICY: 0, REGRESSION: 1, INCONCLUSIVE: 2, INCOMPATIBLE: 3, ERROR: 4, NOT_RUN: 5,
};
export const RegressionVerdictSchema = z.enum(["WITHIN_POLICY", "REGRESSION", "INCONCLUSIVE", "INCOMPATIBLE", "ERROR", "NOT_RUN"]);
const observation = z.number().int().min(0).max(10000000);
const fraction = z.number().finite().min(0).max(1);
const hash = z.string().regex(/^[a-f0-9]{64}$/);
export const RegressionResourceLimitSchema = z.object({
    absolute_increase: observation,
    relative_increase: fraction.describe("Fraction: 0.1 means +10%, 1 means +100%."),
}).strict();
export const RegressionPolicySchema = z.object({
    schema_version: z.literal("ketqat.regression.policy.v1"),
    changed_axes: z.array(z.enum(["source_commit", "circuit", "qiskit"])).max(3),
    resources: z.object({
        depth: RegressionResourceLimitSchema.optional(),
        size: RegressionResourceLimitSchema.optional(),
        two_qubit_gates: RegressionResourceLimitSchema.optional(),
    }).strict(),
    max_total_variation: fraction.nullable(),
    family_alpha: z.number().finite().gt(0).lt(1),
}).strict();
const ChangedFieldSchema = z.enum([
    "source_commit", "source_dirty", "case_id", "circuit_sha256", "factory_sha256",
    "environment.python", "environment.system", "environment.machine", "environment.kernel",
    "environment.ketqat_capture", "environment.qiskit", "environment.numpy", "environment.scipy", "environment.ketqat",
    "conditions.execution", "conditions.initial_state", "conditions.measurement", "conditions.bit_order",
    "conditions.backend", "conditions.noise", "conditions.qubits", "conditions.seed", "conditions.shots",
    "conditions.optimization_level", "conditions.basis_gates",
]);
const status = z.enum(["EXECUTED", "ERROR", "NOT_RUN"]);
const resources = z.object({ depth: observation.optional(), size: observation.optional(), two_qubit_gates: observation.optional() }).strict();
export const RegressionSummarySchema = z.object({
    schema_version: z.literal("ketqat.regression.summary.v1"),
    provenance: z.literal("CLIENT_REPORTED"),
    case_key: hash.describe("SHA-256 of the local case ID; no raw case or repository name."),
    baseline_sha256: hash,
    candidate_sha256: hash,
    baseline_status: status,
    candidate_status: status,
    policy: RegressionPolicySchema,
    changed_fields: z.array(ChangedFieldSchema).max(29),
    resources: z.object({ baseline: resources.nullable(), candidate: resources.nullable() }).strict(),
    distribution: z.object({
        estimate: fraction,
        method: z.enum(["EXACT_IDEAL", "HOEFFDING_ALL_OUTCOMES"]),
        qubits: z.number().int().min(1).max(12),
        baseline_shots: z.number().int().min(1).max(10000000).nullable(),
        candidate_shots: z.number().int().min(1).max(10000000).nullable(),
    }).strict().nullable(),
    verdict: RegressionVerdictSchema,
    exit_code: z.number().int().min(0).max(5),
}).strict();
export function parseRegressionPolicy(input) {
    const policy = RegressionPolicySchema.parse(input);
    if (new Set(policy.changed_axes).size !== policy.changed_axes.length ||
        (!Object.keys(policy.resources).length && policy.max_total_variation === null)) {
        throw new Error("Select unique change axes and at least one measured policy check.");
    }
    return policy;
}
/** Recheck summary arithmetic and verdict consistency, not the private simulation. */
export function inspectRegressionSummary(input) {
    const summary = RegressionSummarySchema.parse(input);
    const policy = parseRegressionPolicy(summary.policy);
    if (new Set(summary.changed_fields).size !== summary.changed_fields.length)
        throw new Error("Repeated comparison field.");
    const permitted = new Set();
    if (policy.changed_axes.includes("source_commit"))
        ["source_commit", "source_dirty", "factory_sha256"].forEach(x => permitted.add(x));
    if (policy.changed_axes.includes("circuit"))
        permitted.add("circuit_sha256");
    if (policy.changed_axes.includes("qiskit"))
        permitted.add("environment.qiskit");
    let verdict;
    const checks = [];
    if (summary.changed_fields.includes("case_id"))
        verdict = "INCOMPATIBLE";
    else if (summary.baseline_status !== "EXECUTED")
        verdict = summary.baseline_status;
    else if (summary.candidate_status !== "EXECUTED")
        verdict = summary.candidate_status;
    else if (summary.changed_fields.some(x => !permitted.has(x)))
        verdict = "INCOMPATIBLE";
    if (verdict && (summary.distribution !== null || summary.resources.baseline !== null || summary.resources.candidate !== null)) {
        throw new Error("A stopped comparison must not carry successful observations.");
    }
    if (!verdict) {
        for (const metric of Object.keys(policy.resources)) {
            const limit = policy.resources[metric];
            const baseline = summary.resources.baseline?.[metric], candidate = summary.resources.candidate?.[metric];
            if (baseline === undefined || candidate === undefined)
                checks.push({ metric, verdict: "INCONCLUSIVE" });
            else {
                const maximum = baseline * (1 + limit.relative_increase) + limit.absolute_increase;
                checks.push({ metric, baseline, candidate, maximum, verdict: candidate > maximum ? "REGRESSION" : "WITHIN_POLICY" });
            }
        }
        if (policy.max_total_variation !== null) {
            const d = summary.distribution;
            if (!d)
                checks.push({ metric: "total_variation", verdict: "INCONCLUSIVE" });
            else {
                let radius = 0;
                if (d.method === "EXACT_IDEAL") {
                    if (d.baseline_shots !== null || d.candidate_shots !== null)
                        throw new Error("Exact probabilities have no shot budget.");
                }
                else {
                    if (!d.baseline_shots || !d.candidate_shots)
                        throw new Error("Sampled observations require both shot budgets.");
                    const k = 2 ** d.qubits, log = Math.log(4 * k / policy.family_alpha);
                    radius = .5 * k * (Math.sqrt(log / (2 * d.baseline_shots)) + Math.sqrt(log / (2 * d.candidate_shots)));
                }
                const lower = Math.max(0, d.estimate - radius), upper = Math.min(1, d.estimate + radius);
                const maximum = policy.max_total_variation;
                checks.push({ metric: "total_variation", estimate: d.estimate, lower, upper, maximum,
                    verdict: upper <= maximum ? "WITHIN_POLICY" : lower > maximum ? "REGRESSION" : "INCONCLUSIVE" });
            }
        }
        else if (summary.distribution !== null)
            throw new Error("Unselected distribution must be redacted.");
        for (const values of [summary.resources.baseline, summary.resources.candidate]) {
            if (values && Object.keys(values).some(x => !(x in policy.resources)))
                throw new Error("Unselected resources must be redacted.");
        }
        verdict = checks.some(x => x.verdict === "REGRESSION") ? "REGRESSION"
            : checks.some(x => x.verdict === "INCONCLUSIVE") ? "INCONCLUSIVE" : "WITHIN_POLICY";
    }
    if (summary.verdict !== verdict || summary.exit_code !== REGRESSION_EXIT_CODES[verdict]) {
        throw new Error("Summary verdict or CI exit code contradicts the declared observations and policy.");
    }
    return { summary, checks };
}
//# sourceMappingURL=regression.js.map
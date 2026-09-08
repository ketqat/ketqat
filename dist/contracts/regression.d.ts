import { z } from "zod";
export declare const REGRESSION_EXIT_CODES: {
    readonly WITHIN_POLICY: 0;
    readonly REGRESSION: 1;
    readonly INCONCLUSIVE: 2;
    readonly INCOMPATIBLE: 3;
    readonly ERROR: 4;
    readonly NOT_RUN: 5;
};
export declare const RegressionVerdictSchema: z.ZodEnum<["WITHIN_POLICY", "REGRESSION", "INCONCLUSIVE", "INCOMPATIBLE", "ERROR", "NOT_RUN"]>;
export declare const RegressionResourceLimitSchema: z.ZodObject<{
    absolute_increase: z.ZodNumber;
    relative_increase: z.ZodNumber;
}, "strict", z.ZodTypeAny, {
    absolute_increase: number;
    relative_increase: number;
}, {
    absolute_increase: number;
    relative_increase: number;
}>;
export declare const RegressionPolicySchema: z.ZodObject<{
    schema_version: z.ZodLiteral<"ketqat.regression.policy.v1">;
    changed_axes: z.ZodArray<z.ZodEnum<["source_commit", "circuit", "qiskit"]>, "many">;
    resources: z.ZodObject<{
        depth: z.ZodOptional<z.ZodObject<{
            absolute_increase: z.ZodNumber;
            relative_increase: z.ZodNumber;
        }, "strict", z.ZodTypeAny, {
            absolute_increase: number;
            relative_increase: number;
        }, {
            absolute_increase: number;
            relative_increase: number;
        }>>;
        size: z.ZodOptional<z.ZodObject<{
            absolute_increase: z.ZodNumber;
            relative_increase: z.ZodNumber;
        }, "strict", z.ZodTypeAny, {
            absolute_increase: number;
            relative_increase: number;
        }, {
            absolute_increase: number;
            relative_increase: number;
        }>>;
        two_qubit_gates: z.ZodOptional<z.ZodObject<{
            absolute_increase: z.ZodNumber;
            relative_increase: z.ZodNumber;
        }, "strict", z.ZodTypeAny, {
            absolute_increase: number;
            relative_increase: number;
        }, {
            absolute_increase: number;
            relative_increase: number;
        }>>;
    }, "strict", z.ZodTypeAny, {
        depth?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        size?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        two_qubit_gates?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
    }, {
        depth?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        size?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        two_qubit_gates?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
    }>;
    max_total_variation: z.ZodNullable<z.ZodNumber>;
    family_alpha: z.ZodNumber;
}, "strict", z.ZodTypeAny, {
    schema_version: "ketqat.regression.policy.v1";
    changed_axes: ("circuit" | "qiskit" | "source_commit")[];
    resources: {
        depth?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        size?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        two_qubit_gates?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
    };
    max_total_variation: number | null;
    family_alpha: number;
}, {
    schema_version: "ketqat.regression.policy.v1";
    changed_axes: ("circuit" | "qiskit" | "source_commit")[];
    resources: {
        depth?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        size?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
        two_qubit_gates?: {
            absolute_increase: number;
            relative_increase: number;
        } | undefined;
    };
    max_total_variation: number | null;
    family_alpha: number;
}>;
export type RegressionPolicy = z.infer<typeof RegressionPolicySchema>;
export declare const RegressionSummarySchema: z.ZodObject<{
    schema_version: z.ZodLiteral<"ketqat.regression.summary.v1">;
    provenance: z.ZodLiteral<"CLIENT_REPORTED">;
    case_key: z.ZodString;
    baseline_sha256: z.ZodString;
    candidate_sha256: z.ZodString;
    baseline_status: z.ZodEnum<["EXECUTED", "ERROR", "NOT_RUN"]>;
    candidate_status: z.ZodEnum<["EXECUTED", "ERROR", "NOT_RUN"]>;
    policy: z.ZodObject<{
        schema_version: z.ZodLiteral<"ketqat.regression.policy.v1">;
        changed_axes: z.ZodArray<z.ZodEnum<["source_commit", "circuit", "qiskit"]>, "many">;
        resources: z.ZodObject<{
            depth: z.ZodOptional<z.ZodObject<{
                absolute_increase: z.ZodNumber;
                relative_increase: z.ZodNumber;
            }, "strict", z.ZodTypeAny, {
                absolute_increase: number;
                relative_increase: number;
            }, {
                absolute_increase: number;
                relative_increase: number;
            }>>;
            size: z.ZodOptional<z.ZodObject<{
                absolute_increase: z.ZodNumber;
                relative_increase: z.ZodNumber;
            }, "strict", z.ZodTypeAny, {
                absolute_increase: number;
                relative_increase: number;
            }, {
                absolute_increase: number;
                relative_increase: number;
            }>>;
            two_qubit_gates: z.ZodOptional<z.ZodObject<{
                absolute_increase: z.ZodNumber;
                relative_increase: z.ZodNumber;
            }, "strict", z.ZodTypeAny, {
                absolute_increase: number;
                relative_increase: number;
            }, {
                absolute_increase: number;
                relative_increase: number;
            }>>;
        }, "strict", z.ZodTypeAny, {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        }, {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        }>;
        max_total_variation: z.ZodNullable<z.ZodNumber>;
        family_alpha: z.ZodNumber;
    }, "strict", z.ZodTypeAny, {
        schema_version: "ketqat.regression.policy.v1";
        changed_axes: ("circuit" | "qiskit" | "source_commit")[];
        resources: {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        };
        max_total_variation: number | null;
        family_alpha: number;
    }, {
        schema_version: "ketqat.regression.policy.v1";
        changed_axes: ("circuit" | "qiskit" | "source_commit")[];
        resources: {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        };
        max_total_variation: number | null;
        family_alpha: number;
    }>;
    changed_fields: z.ZodArray<z.ZodEnum<["source_commit", "source_dirty", "case_id", "circuit_sha256", "factory_sha256", "environment.python", "environment.system", "environment.machine", "environment.kernel", "environment.ketqat_capture", "environment.qiskit", "environment.numpy", "environment.scipy", "environment.ketqat", "conditions.execution", "conditions.initial_state", "conditions.measurement", "conditions.bit_order", "conditions.backend", "conditions.noise", "conditions.qubits", "conditions.seed", "conditions.shots", "conditions.optimization_level", "conditions.basis_gates"]>, "many">;
    resources: z.ZodObject<{
        baseline: z.ZodNullable<z.ZodObject<{
            depth: z.ZodOptional<z.ZodNumber>;
            size: z.ZodOptional<z.ZodNumber>;
            two_qubit_gates: z.ZodOptional<z.ZodNumber>;
        }, "strict", z.ZodTypeAny, {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        }, {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        }>>;
        candidate: z.ZodNullable<z.ZodObject<{
            depth: z.ZodOptional<z.ZodNumber>;
            size: z.ZodOptional<z.ZodNumber>;
            two_qubit_gates: z.ZodOptional<z.ZodNumber>;
        }, "strict", z.ZodTypeAny, {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        }, {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        }>>;
    }, "strict", z.ZodTypeAny, {
        baseline: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
        candidate: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
    }, {
        baseline: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
        candidate: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
    }>;
    distribution: z.ZodNullable<z.ZodObject<{
        estimate: z.ZodNumber;
        method: z.ZodEnum<["EXACT_IDEAL", "HOEFFDING_ALL_OUTCOMES"]>;
        qubits: z.ZodNumber;
        baseline_shots: z.ZodNullable<z.ZodNumber>;
        candidate_shots: z.ZodNullable<z.ZodNumber>;
    }, "strict", z.ZodTypeAny, {
        estimate: number;
        method: "EXACT_IDEAL" | "HOEFFDING_ALL_OUTCOMES";
        qubits: number;
        baseline_shots: number | null;
        candidate_shots: number | null;
    }, {
        estimate: number;
        method: "EXACT_IDEAL" | "HOEFFDING_ALL_OUTCOMES";
        qubits: number;
        baseline_shots: number | null;
        candidate_shots: number | null;
    }>>;
    verdict: z.ZodEnum<["WITHIN_POLICY", "REGRESSION", "INCONCLUSIVE", "INCOMPATIBLE", "ERROR", "NOT_RUN"]>;
    exit_code: z.ZodNumber;
}, "strict", z.ZodTypeAny, {
    schema_version: "ketqat.regression.summary.v1";
    provenance: "CLIENT_REPORTED";
    case_key: string;
    baseline_sha256: string;
    candidate_sha256: string;
    baseline_status: "ERROR" | "EXECUTED" | "NOT_RUN";
    candidate_status: "ERROR" | "EXECUTED" | "NOT_RUN";
    policy: {
        schema_version: "ketqat.regression.policy.v1";
        changed_axes: ("circuit" | "qiskit" | "source_commit")[];
        resources: {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        };
        max_total_variation: number | null;
        family_alpha: number;
    };
    changed_fields: ("case_id" | "circuit_sha256" | "conditions.backend" | "conditions.basis_gates" | "conditions.bit_order" | "conditions.execution" | "conditions.initial_state" | "conditions.measurement" | "conditions.noise" | "conditions.optimization_level" | "conditions.qubits" | "conditions.seed" | "conditions.shots" | "environment.kernel" | "environment.ketqat" | "environment.ketqat_capture" | "environment.machine" | "environment.numpy" | "environment.python" | "environment.qiskit" | "environment.scipy" | "environment.system" | "factory_sha256" | "source_commit" | "source_dirty")[];
    resources: {
        baseline: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
        candidate: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
    };
    distribution: {
        estimate: number;
        method: "EXACT_IDEAL" | "HOEFFDING_ALL_OUTCOMES";
        qubits: number;
        baseline_shots: number | null;
        candidate_shots: number | null;
    } | null;
    verdict: "ERROR" | "INCOMPATIBLE" | "INCONCLUSIVE" | "NOT_RUN" | "REGRESSION" | "WITHIN_POLICY";
    exit_code: number;
}, {
    schema_version: "ketqat.regression.summary.v1";
    provenance: "CLIENT_REPORTED";
    case_key: string;
    baseline_sha256: string;
    candidate_sha256: string;
    baseline_status: "ERROR" | "EXECUTED" | "NOT_RUN";
    candidate_status: "ERROR" | "EXECUTED" | "NOT_RUN";
    policy: {
        schema_version: "ketqat.regression.policy.v1";
        changed_axes: ("circuit" | "qiskit" | "source_commit")[];
        resources: {
            depth?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            size?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
            two_qubit_gates?: {
                absolute_increase: number;
                relative_increase: number;
            } | undefined;
        };
        max_total_variation: number | null;
        family_alpha: number;
    };
    changed_fields: ("case_id" | "circuit_sha256" | "conditions.backend" | "conditions.basis_gates" | "conditions.bit_order" | "conditions.execution" | "conditions.initial_state" | "conditions.measurement" | "conditions.noise" | "conditions.optimization_level" | "conditions.qubits" | "conditions.seed" | "conditions.shots" | "environment.kernel" | "environment.ketqat" | "environment.ketqat_capture" | "environment.machine" | "environment.numpy" | "environment.python" | "environment.qiskit" | "environment.scipy" | "environment.system" | "factory_sha256" | "source_commit" | "source_dirty")[];
    resources: {
        baseline: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
        candidate: {
            depth?: number | undefined;
            size?: number | undefined;
            two_qubit_gates?: number | undefined;
        } | null;
    };
    distribution: {
        estimate: number;
        method: "EXACT_IDEAL" | "HOEFFDING_ALL_OUTCOMES";
        qubits: number;
        baseline_shots: number | null;
        candidate_shots: number | null;
    } | null;
    verdict: "ERROR" | "INCOMPATIBLE" | "INCONCLUSIVE" | "NOT_RUN" | "REGRESSION" | "WITHIN_POLICY";
    exit_code: number;
}>;
export type RegressionSummary = z.infer<typeof RegressionSummarySchema>;
export type RegressionVerdict = z.infer<typeof RegressionVerdictSchema>;
export type RegressionCheck = {
    metric: "depth" | "size" | "two_qubit_gates" | "total_variation";
    verdict: "WITHIN_POLICY" | "REGRESSION" | "INCONCLUSIVE";
    baseline?: number;
    candidate?: number;
    maximum?: number;
    estimate?: number;
    lower?: number;
    upper?: number;
};
export declare function parseRegressionPolicy(input: unknown): RegressionPolicy;
/** Recheck summary arithmetic and verdict consistency, not the private simulation. */
export declare function inspectRegressionSummary(input: unknown): {
    summary: RegressionSummary;
    checks: RegressionCheck[];
};
//# sourceMappingURL=regression.d.ts.map
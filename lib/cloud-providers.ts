
export interface QuantumProvider {
    id: string;
    name: string;
    url: string;
    description: string;
    category: "Hardware" | "Software" | "Cloud";
}

export const QUANTUM_PROVIDERS: QuantumProvider[] = [
    {
        id: "iqm-resonance",
        name: "IQM Resonance",
        url: "https://resonance.meetiqm.com/",
        description: "Access IQM's superconducting quantum computers and simulators directly through the Resonance cloud platform.",
        category: "Hardware",
    },
    {
        id: "dwave-leap",
        name: "D-Wave Leap",
        url: "https://cloud.dwavesys.com/leap/login",
        description: "Real-time access to D-Wave's quantum annealing processors and hybrid solvers for optimization problems.",
        category: "Hardware",
    },
    {
        id: "ionq-cloud",
        name: "IonQ Cloud",
        url: "https://cloud.ionq.com/jobs",
        description: "Run circuits on high-fidelity trapped-ion quantum computers via the IonQ Cloud portal.",
        category: "Hardware",
    },
    {
        id: "quantinuum-nexus",
        name: "Quantinuum Nexus",
        url: "https://nexus.quantinuum.com/",
        description: "A comprehensive platform for managing and executing experiments on H-Series trapped-ion quantum backend.",
        category: "Hardware",
    },
    {
        id: "pasqal-cloud",
        name: "Pasqal Cloud",
        url: "https://portal.pasqal.cloud/dashboard",
        description: "Control neutral atom quantum processors for simulation and optimization tasks via Pasqal's interface.",
        category: "Hardware",
    },
    {
        id: "quandela-cloud",
        name: "Quandela Cloud",
        url: "https://cloud.quandela.com/webide/",
        description: "Photonic quantum computing cloud platform featuring Perceval for optical quantum simulation and execution.",
        category: "Hardware",
    },
    {
        id: "classiq-platform",
        name: "Classiq Platform",
        url: "https://platform.classiq.io/",
        description: "A high-level synthesis engine that automatically generates optimized quantum circuits from functional models.",
        category: "Software",
    },
    {
        id: "bluequbit",
        name: "BlueQubit",
        url: "https://app.bluequbit.io/",
        description: "High-performance quantum simulators enabling fast execution of complex quantum circuits on CPU/GPU clusters.",
        category: "Software",
    },
    {
        id: "quantum-rings",
        name: "Quantum Rings",
        url: "https://portal.quantumrings.com/",
        description: "Advanced quantum simulation platform designed to run large-scale quantum algorithms on classical hardware.",
        category: "Software",
    },
    {
        id: "q-ctrl-black",
        name: "Q-CTRL Black",
        url: "https://black.q-ctrl.com/welcome",
        description: "Infrastructure software to improve quantum hardware performance through advanced control and error suppression.",
        category: "Software",
    },
    {
        id: "riverlane-deltakit",
        name: "Riverlane Deltakit",
        url: "https://deltakit.riverlane.com/",
        description: "Tools for quantum error correction, enabling the development and testing of fault-tolerant quantum architectures.",
        category: "Software",
    },
    {
        id: "entropica-labs-loom",
        name: "Entropica Labs Loom",
        url: "https://loom-docs.entropicalabs.com/",
        description: "Development tools and middleware for designing and running algorithms on fault-tolerant quantum computers.",
        category: "Software",
    },
    {
        id: "qbraid",
        name: "qBraid",
        url: "https://account.qbraid.com/",
        description: "A comprehensive cloud platform for developing, running, and deploying quantum jobs across various hardware providers using a unified interface.",
        category: "Cloud",
    },
];

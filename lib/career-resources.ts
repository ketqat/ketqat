export interface CareerResource {
    id: string;
    name: string;
    url: string;
    description: string;
    category: "Career" | "Community";
}

export const CAREER_RESOURCES: CareerResource[] = [
    {
        id: "aqora",
        name: "Aqora",
        url: "https://aqora.io/",
        description: "Solve quantum coding challenges and find jobs in the quantum computing industry.",
        category: "Community",
    },
    {
        id: "quantum-jobs-list",
        name: "Quantum Jobs List",
        url: "https://www.quantumjobslist.com/",
        description: "The leading job board for the quantum industry, featuring roles from around the globe.",
        category: "Career",
    },
    {
        id: "quantum-jobs",
        name: "Quantum Jobs",
        url: "https://www.quantumjobs.us/",
        description: "Find your next role in quantum computing and technology with tailored listings.",
        category: "Career",
    },
    {
        id: "quantum-computing-jobs-uk",
        name: "Quantum Computing Jobs UK",
        url: "https://quantumcomputingjobs.co.uk/",
        description: "Dedicated job listings for the UK quantum sector, connecting talent with opportunities.",
        category: "Career",
    },
    {
        id: "quantum-industry-canada",
        name: "Quantum Industry Canada",
        url: "https://www.quantumindustrycanada.ca/jobs/",
        description: "Job opportunities within the Canadian quantum ecosystem and member companies.",
        category: "Career",
    },
];

import { QUANTUM_PROVIDERS } from "@/lib/cloud-providers"
import { ProviderCard } from "@/components/cloud/provider-card"

export default function CloudHubPage() {
    return (
        <div className="container py-10 mx-auto">
            <div className="mb-8 space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Quantum Cloud Hub</h1>
                <p className="text-lg text-muted-foreground">
                    Connect and manage your quantum infrastructure in one place.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {QUANTUM_PROVIDERS.map((provider) => (
                    <ProviderCard key={provider.id} provider={provider} />
                ))}
            </div>
        </div>
    )
}

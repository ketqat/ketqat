"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { QUANTUM_PROVIDERS } from "@/lib/cloud-providers"
import { ProviderCard } from "@/components/cloud/provider-card"

import { ArrowRight } from "lucide-react"

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-quantum-blue to-quantum-orange bg-clip-text text-transparent">
            The Home for Quantum Error Correction
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Discover, share, and collaborate on QEC decoders, quantum circuits, and noise data.
            Join the open-source quantum computing community.
          </p>
        </div>
      </section>

      {/* Quantum Cloud Hub Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold">Quantum Cloud Hub</h2>
            <p className="text-muted-foreground mt-2">
              Connect and manage your quantum infrastructure.
            </p>
          </div>
          <Button
            variant="ghost"
            onClick={() => router.push("/cloud")}
            className="gap-2"
          >
            View All Providers
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {QUANTUM_PROVIDERS.map((provider) => (
            <ProviderCard key={provider.id} provider={provider} />
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-12 bg-muted/50 rounded-lg my-12">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why KetQat?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl mb-4">🔬</div>
              <h3 className="text-xl font-semibold mb-2">Research-Focused</h3>
              <p className="text-muted-foreground">
                Built by researchers, for researchers. Share your latest QEC innovations.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🌐</div>
              <h3 className="text-xl font-semibold mb-2">Open Source</h3>
              <p className="text-muted-foreground">
                All decoders and tools are open-source and freely available.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-xl font-semibold mb-2">Collaborative</h3>
              <p className="text-muted-foreground">
                Collaborate with the global quantum computing community.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}


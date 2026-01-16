"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { QUANTUM_PROVIDERS } from "@/lib/cloud-providers"
import { ProviderCard } from "@/components/cloud/provider-card"

import { ArrowRight, Github } from "lucide-react"

export default function HomePage() {
  const router = useRouter()
  const [selectedTab, setSelectedTab] = useState("all")

  const allProviders = QUANTUM_PROVIDERS
  const hardwareProviders = QUANTUM_PROVIDERS.filter(provider => provider.category === "Hardware")
  const softwareProviders = QUANTUM_PROVIDERS.filter(provider => provider.category === "Software")
  const cloudProviders = QUANTUM_PROVIDERS.filter(provider => provider.category === "Cloud")

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="flex items-center justify-center gap-4 text-5xl md:text-6xl font-bold mb-6">
            <Image 
              src="/ketqat-icon.png" 
              alt="KetQat" 
              width={64} 
              height={64}
              className="object-contain"
            />
            <span className="bg-gradient-to-r from-quantum-blue to-quantum-orange bg-clip-text text-transparent">
              The Home for Quantum Computing
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Discover cloud providers, run algorithms, and collaborate on the future of quantum technology. Join the open-source community.
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
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="all">All Providers</TabsTrigger>
            <TabsTrigger value="hardware">Hardware</TabsTrigger>
            <TabsTrigger value="software">Software</TabsTrigger>
            <TabsTrigger value="cloud">Cloud</TabsTrigger>
          </TabsList>
          <TabsContent value="all" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {allProviders.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </TabsContent>
          <TabsContent value="hardware" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {hardwareProviders.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </TabsContent>
          <TabsContent value="software" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {softwareProviders.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </TabsContent>
          <TabsContent value="cloud" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {cloudProviders.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
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

      {/* Get Involved Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Get Involved</h2>
          <p className="text-lg text-muted-foreground mb-8">
            Fork us on GitHub and help build the future of quantum computing. 
            We encourage you to fork this repository and contribute to the open-source project.
          </p>
          <div className="flex justify-center gap-4">
            <Button
              size="lg"
              className="gap-2"
              asChild
            >
              <a 
                href="https://github.com/ketqat/ketqat" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                <Github className="h-5 w-5" />
                Fork on GitHub
              </a>
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="gap-2"
              onClick={() => router.push("/cloud")}
            >
              View Cloud Hub
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}


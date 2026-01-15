"use client"

import { ExternalLink, Cpu, Code, Cloud, Zap } from "lucide-react"
import { QuantumProvider } from "@/lib/cloud-providers"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ConnectDialog } from "./connect-dialog"
import { cn } from "@/lib/utils"

interface ProviderCardProps {
    provider: QuantumProvider
}

export function ProviderCard({ provider }: ProviderCardProps) {
    const getIcon = (category: string) => {
        switch (category) {
            case "Hardware":
                return <Cpu className="h-5 w-5 text-blue-500" />
            case "Software":
                return <Code className="h-5 w-5 text-green-500" />
            case "Cloud":
                return <Cloud className="h-5 w-5 text-purple-500" />
            default:
                return <Zap className="h-5 w-5 text-yellow-500" />
        }
    }

    const getBadgeVariant = (category: string) => {
        switch (category) {
            case "Hardware":
                return "default" // usually primary color
            case "Software":
                return "secondary"
            default:
                return "outline"
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case "operational":
                return "bg-green-500"
            case "degraded":
                return "bg-yellow-500"
            case "maintenance":
                return "bg-red-500"
            default:
                return "bg-gray-500"
        }
    }

    const getPricingVariant = (pricing: string) => {
        switch (pricing) {
            case "Free Tier":
                return "default"
            case "Paid":
                return "secondary"
            case "Contact":
                return "outline"
            default:
                return "outline"
        }
    }

    return (
        <Card className="flex flex-col h-full hover:shadow-md transition-shadow relative">
            {/* Status Indicator */}
            <div className={cn("absolute top-4 right-4 w-2 h-2 rounded-full", getStatusColor(provider.status))} 
                 title={provider.status.charAt(0).toUpperCase() + provider.status.slice(1)} />
            
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 pr-8">
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                    <div className="p-2 bg-muted rounded-full">
                        {getIcon(provider.category)}
                    </div>
                    {provider.name}
                </CardTitle>
                <Badge variant={getBadgeVariant(provider.category) as any}>
                    {provider.category}
                </Badge>
            </CardHeader>
            <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed mb-3">
                    {provider.description}
                </p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-1.5 mb-3">
                    {provider.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                        </Badge>
                    ))}
                </div>

                {/* Pricing */}
                <div className="mt-auto">
                    <Badge variant={getPricingVariant(provider.pricing) as any} className="text-xs">
                        {provider.pricing}
                    </Badge>
                </div>
            </CardContent>
            <CardFooter className="flex justify-between pt-4 border-t">
                <ConnectDialog providerName={provider.name} />
                <Button variant="ghost" size="sm" className="gap-2" asChild>
                    <a href={provider.url} target="_blank" rel="noopener noreferrer">
                        Launch
                        <ExternalLink className="h-4 w-4" />
                    </a>
                </Button>
            </CardFooter>
        </Card>
    )
}

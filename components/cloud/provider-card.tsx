"use client"

import { ExternalLink, Cpu, Code, Cloud, Zap } from "lucide-react"
import { QuantumProvider } from "@/lib/cloud-providers"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ConnectDialog } from "./connect-dialog"

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

    return (
        <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
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
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                    {provider.description}
                </p>
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

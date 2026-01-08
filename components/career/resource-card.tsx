"use client"

import { Briefcase, Users, ExternalLink } from "lucide-react"
import { CareerResource } from "@/lib/career-resources"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface ResourceCardProps {
    resource: CareerResource
}

export function ResourceCard({ resource }: ResourceCardProps) {
    const getIcon = (category: string) => {
        switch (category) {
            case "Career":
                return <Briefcase className="h-5 w-5 text-indigo-500" />
            case "Community":
                return <Users className="h-5 w-5 text-teal-500" />
            default:
                return <Briefcase className="h-5 w-5 text-indigo-500" />
        }
    }

    const getBadgeVariant = (category: string) => {
        switch (category) {
            case "Career":
                return "secondary"
            case "Community":
                return "outline"
            default:
                return "default"
        }
    }

    return (
        <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                    <div className="p-2 bg-muted rounded-full">
                        {getIcon(resource.category)}
                    </div>
                    {resource.name}
                </CardTitle>
                <Badge variant={getBadgeVariant(resource.category) as any}>
                    {resource.category}
                </Badge>
            </CardHeader>
            <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                    {resource.description}
                </p>
            </CardContent>
            <CardFooter className="pt-4 border-t">
                <Button variant="ghost" size="sm" className="w-full gap-2" asChild>
                    <a href={resource.url} target="_blank" rel="noopener noreferrer">
                        Visit Website
                        <ExternalLink className="h-4 w-4" />
                    </a>
                </Button>
            </CardFooter>
        </Card>
    )
}

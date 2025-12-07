"use client"

import Link from "next/link"
import { Star, Download, Tag } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Decoder } from "@/lib/types"

interface DecoderCardProps {
  decoder: Decoder
}

export function DecoderCard({ decoder }: DecoderCardProps) {
  return (
    <Link href={`/decoders/${decoder.id}`}>
      <Card className="h-full transition-all hover:shadow-lg hover:scale-[1.02] cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle className="text-xl">{decoder.title}</CardTitle>
          </div>
          <CardDescription className="line-clamp-2 mt-2">
            {decoder.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span>{decoder.stars.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-1">
              <Download className="h-4 w-4" />
              <span>{decoder.downloads.toLocaleString()}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {decoder.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {decoder.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{decoder.tags.length - 3}
              </Badge>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">by {decoder.author}</span>
          {decoder.language && (
            <Badge variant="secondary" className="text-xs">
              {decoder.language}
            </Badge>
          )}
        </CardFooter>
      </Card>
    </Link>
  )
}


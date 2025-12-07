"use client"

import { notFound } from "next/navigation"
import { Star, Download, Calendar, Code, FileText, Users } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getDecoderById } from "@/lib/mock-data"

interface DecoderDetailPageProps {
  params: {
    id: string
  }
}

export default function DecoderDetailPage({ params }: DecoderDetailPageProps) {
  const decoder = getDecoderById(params.id)

  if (!decoder) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">{decoder.title}</h1>
        <p className="text-lg text-muted-foreground mb-4">{decoder.description}</p>
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <span className="font-medium">by</span>
            <span className="text-quantum-blue">{decoder.author}</span>
          </div>
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span>{decoder.stars.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <Download className="h-4 w-4" />
            <span>{decoder.downloads.toLocaleString()}</span>
          </div>
          {decoder.language && (
            <Badge variant="secondary">{decoder.language}</Badge>
          )}
          {decoder.license && (
            <Badge variant="outline">{decoder.license}</Badge>
          )}
        </div>
        <div className="flex flex-wrap gap-2 mt-4">
          {decoder.tags.map((tag) => (
            <Badge key={tag} variant="outline">
              {tag}
            </Badge>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="model-card" className="w-full">
        <TabsList>
          <TabsTrigger value="model-card">
            <FileText className="h-4 w-4 mr-2" />
            Model Card
          </TabsTrigger>
          <TabsTrigger value="files">
            <Code className="h-4 w-4 mr-2" />
            Files
          </TabsTrigger>
          <TabsTrigger value="community">
            <Users className="h-4 w-4 mr-2" />
            Community
          </TabsTrigger>
        </TabsList>

        <TabsContent value="model-card" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Model Card</CardTitle>
              <CardDescription>Detailed information about this decoder</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Description</h3>
                <p className="text-muted-foreground">{decoder.description}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Specifications</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-muted-foreground">Code Type:</span>
                    <p className="font-medium capitalize">{decoder.codeType.replace("-", " ")}</p>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Qubit Type:</span>
                    <p className="font-medium capitalize">{decoder.qubitType.replace("-", " ")}</p>
                  </div>
                  {decoder.distance && (
                    <div>
                      <span className="text-sm text-muted-foreground">Code Distance:</span>
                      <p className="font-medium">{decoder.distance}</p>
                    </div>
                  )}
                  {decoder.language && (
                    <div>
                      <span className="text-sm text-muted-foreground">Language:</span>
                      <p className="font-medium">{decoder.language}</p>
                    </div>
                  )}
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Metadata</h3>
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>Created: {new Date(decoder.createdAt).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>Updated: {new Date(decoder.updatedAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="files" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Files</CardTitle>
              <CardDescription>Source code and related files</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Code className="h-4 w-4 text-muted-foreground" />
                      <span className="font-mono">decoder.py</span>
                    </div>
                    <span className="text-sm text-muted-foreground">12.5 KB</span>
                  </div>
                </div>
                <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="font-mono">README.md</span>
                    </div>
                    <span className="text-sm text-muted-foreground">2.1 KB</span>
                  </div>
                </div>
                <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="font-mono">requirements.txt</span>
                    </div>
                    <span className="text-sm text-muted-foreground">0.5 KB</span>
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                This is a placeholder. In a full implementation, this would show the actual repository files.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="community" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Community</CardTitle>
              <CardDescription>Discussions and contributions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Community features coming soon. This will include discussions, issues, and contributions.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}


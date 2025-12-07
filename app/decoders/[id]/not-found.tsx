import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="container mx-auto px-4 py-20 text-center">
      <h1 className="text-4xl font-bold mb-4">Decoder Not Found</h1>
      <p className="text-muted-foreground mb-8">
        The decoder you're looking for doesn't exist or has been removed.
      </p>
      <div className="flex gap-4 justify-center">
        <Button asChild>
          <Link href="/decoders">Browse All Decoders</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/">Go Home</Link>
        </Button>
      </div>
    </div>
  )
}


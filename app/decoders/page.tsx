"use client"

import { useState, useMemo } from "react"
import { useSearchParams } from "next/navigation"
import { SearchBar } from "@/components/SearchBar"
import { FilterBar } from "@/components/FilterBar"
import { DecoderCard } from "@/components/DecoderCard"
import { mockDecoders } from "@/lib/mock-data"
import { CodeType, QubitType } from "@/lib/types"

export default function DecodersPage() {
  const searchParams = useSearchParams()
  const initialSearch = searchParams.get("search") || ""
  
  const [searchQuery, setSearchQuery] = useState(initialSearch)
  const [codeTypeFilter, setCodeTypeFilter] = useState<CodeType | "all">("all")
  const [qubitTypeFilter, setQubitTypeFilter] = useState<QubitType | "all">("all")

  const filteredDecoders = useMemo(() => {
    return mockDecoders.filter((decoder) => {
      // Search filter
      const matchesSearch =
        searchQuery === "" ||
        decoder.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        decoder.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        decoder.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        decoder.tags.some((tag) =>
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        )

      // Code type filter
      const matchesCodeType =
        codeTypeFilter === "all" || decoder.codeType === codeTypeFilter

      // Qubit type filter
      const matchesQubitType =
        qubitTypeFilter === "all" ||
        decoder.qubitType === qubitTypeFilter ||
        decoder.qubitType === "all"

      return matchesSearch && matchesCodeType && matchesQubitType
    })
  }, [searchQuery, codeTypeFilter, qubitTypeFilter])

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Decoder Zoo</h1>
        <p className="text-muted-foreground">
          Discover and explore Quantum Error Correction decoders from the community
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-6">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search decoders by name, author, or tags..."
        />
        <FilterBar
          codeType={codeTypeFilter}
          qubitType={qubitTypeFilter}
          onCodeTypeChange={setCodeTypeFilter}
          onQubitTypeChange={setQubitTypeFilter}
        />
      </div>

      {/* Results Count */}
      <div className="mb-6">
        <p className="text-sm text-muted-foreground">
          {filteredDecoders.length} decoder{filteredDecoders.length !== 1 ? "s" : ""} found
        </p>
      </div>

      {/* Decoder Grid */}
      {filteredDecoders.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDecoders.map((decoder) => (
            <DecoderCard key={decoder.id} decoder={decoder} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-lg text-muted-foreground mb-4">
            No decoders found matching your criteria
          </p>
          <p className="text-sm text-muted-foreground">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </div>
  )
}


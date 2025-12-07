"use client"

import { Select } from "@/components/ui/select"
import { QubitType, CodeType } from "@/lib/types"

interface FilterBarProps {
  codeType: CodeType | "all"
  qubitType: QubitType | "all"
  onCodeTypeChange: (value: CodeType | "all") => void
  onQubitTypeChange: (value: QubitType | "all") => void
}

export function FilterBar({
  codeType,
  qubitType,
  onCodeTypeChange,
  onQubitTypeChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4">
      <div className="flex-1">
        <label className="text-sm font-medium mb-2 block">Code Type</label>
        <Select
          value={codeType}
          onChange={(e) => onCodeTypeChange(e.target.value as CodeType | "all")}
        >
          <option value="all">All Code Types</option>
          <option value="surface-code">Surface Code</option>
          <option value="color-code">Color Code</option>
          <option value="stabilizer">Stabilizer</option>
          <option value="bosonic">Bosonic</option>
        </Select>
      </div>
      <div className="flex-1">
        <label className="text-sm font-medium mb-2 block">Qubit Type</label>
        <Select
          value={qubitType}
          onChange={(e) => onQubitTypeChange(e.target.value as QubitType | "all")}
        >
          <option value="all">All Qubit Types</option>
          <option value="superconducting">Superconducting</option>
          <option value="trapped-ion">Trapped Ion</option>
          <option value="photonic">Photonic</option>
          <option value="neutral-atom">Neutral Atom</option>
        </Select>
      </div>
    </div>
  )
}


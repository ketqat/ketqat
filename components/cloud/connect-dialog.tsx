"use client"

import { useState } from "react"
import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label" // Assuming Label might be needed, but if not I'll just use standard label or skip if Input handles it. Shadcn usually has a Label component. 
// Wait, I didn't check for Label. I'll just use HTML label for now to avoid errors if Label component is missing.

export function ConnectDialog({ providerName }: { providerName: string }) {
    const [apiKey, setApiKey] = useState("")
    const [isOpen, setIsOpen] = useState(false)
    const [isSaving, setIsSaving] = useState(false)

    const handleSave = () => {
        setIsSaving(true)
        // Mock save action
        setTimeout(() => {
            setIsSaving(false)
            setIsOpen(false)
            setApiKey("")
            // alert(`Connected to ${providerName}!`) // Optional: could show a toast if available, but alert is annoying.
            console.log(`Connected to ${providerName} with key: ${apiKey}`)
        }, 1000)
    }

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                    <Settings className="h-4 w-4" />
                    Connect
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Connect to {providerName}</DialogTitle>
                    <DialogDescription>
                        Enter your API credentials to access this provider's services.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <label htmlFor="apiKey" className="text-right text-sm font-medium">
                            API Key
                        </label>
                        <Input
                            id="apiKey"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="col-span-3"
                            placeholder="qk_..."
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button type="submit" onClick={handleSave} disabled={isSaving}>
                        {isSaving ? "Saving..." : "Save Connection"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}

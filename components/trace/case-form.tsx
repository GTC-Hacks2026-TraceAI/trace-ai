"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Spinner } from "@/components/ui/spinner"
import { createCase } from "@/lib/api"
import type { CaseInput } from "@/lib/types"
import { UserPlus, MapPin, Clock, Shirt, Backpack } from "lucide-react"

export function CaseForm() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState<CaseInput>({
    subject_name: "",
    approximate_age: undefined,
    description: "",
    last_known_location: "",
    last_known_time: "",
    clothing_description: "",
    accessories: "",
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "approximate_age" ? (value ? parseInt(value) : undefined) : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const newCase = await createCase(formData)
      router.push(`/cases/${newCase.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create case")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UserPlus className="h-5 w-5" />
          Create New Case
        </CardTitle>
        <CardDescription>
          Enter details about the missing person to begin the investigation.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="subject_name">Subject Name *</Label>
              <Input
                id="subject_name"
                name="subject_name"
                placeholder="Full name of missing person"
                value={formData.subject_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="approximate_age">Approximate Age</Label>
              <Input
                id="approximate_age"
                name="approximate_age"
                type="number"
                placeholder="Estimated age"
                value={formData.approximate_age ?? ""}
                onChange={handleChange}
                min={0}
                max={120}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              name="description"
              placeholder="Physical description (height, build, hair color, distinguishing features...)"
              value={formData.description}
              onChange={handleChange}
              required
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="last_known_location" className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Last Known Location *
              </Label>
              <Input
                id="last_known_location"
                name="last_known_location"
                placeholder="Building, street, or area"
                value={formData.last_known_location}
                onChange={handleChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="last_known_time" className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Last Seen Time *
              </Label>
              <Input
                id="last_known_time"
                name="last_known_time"
                type="datetime-local"
                value={formData.last_known_time}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="clothing_description" className="flex items-center gap-2">
                <Shirt className="h-4 w-4" />
                Clothing Description
              </Label>
              <Input
                id="clothing_description"
                name="clothing_description"
                placeholder="Shirt, pants, shoes, jacket..."
                value={formData.clothing_description ?? ""}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="accessories" className="flex items-center gap-2">
                <Backpack className="h-4 w-4" />
                Accessories
              </Label>
              <Input
                id="accessories"
                name="accessories"
                placeholder="Backpack, bag, glasses, watch..."
                value={formData.accessories ?? ""}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2 text-xs text-muted-foreground">
            <div className="h-4 w-4 rounded border border-dashed border-muted-foreground/50 flex items-center justify-center text-[10px]">
              +
            </div>
            Image upload available in future release
          </div>

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Spinner className="mr-2 h-4 w-4" />
                Creating Case...
              </>
            ) : (
              "Create Case"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

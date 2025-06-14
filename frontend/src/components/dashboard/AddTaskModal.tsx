import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { User, RoleType, Task } from '@/types'
import { taskApi } from '@/lib/api'

interface AddTaskModalProps {
  open: boolean
  onClose: () => void
  user: User
  onTaskCreated?: (task: Task) => void
}

export default function AddTaskModal({ open, onClose, user, onTaskCreated }: AddTaskModalProps) {
  const [description, setDescription] = useState('')
  const [assignedRole, setAssignedRole] = useState<RoleType>('CEO')
  const [loading, setLoading] = useState(false)

  if (!open) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim()) return

    try {
      setLoading(true)
      const newTask = await taskApi.create({
        user_id: user.id,
        assigned_to_role: assignedRole,
        description,
        status: 'pending',
      } as any)

      onTaskCreated && onTaskCreated(newTask)
      window.dispatchEvent(new CustomEvent('task_created', { detail: newTask }))
      setDescription('')
      onClose()
    } catch (err) {
      console.error('Failed to create task:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>Add New Task</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <Input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Define MVP feature list"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Assign to</label>
              <select
                className="w-full border rounded px-3 py-2 text-sm"
                value={assignedRole}
                onChange={(e) => setAssignedRole(e.target.value as RoleType)}
              >
                {(['CEO', 'CTO', 'CMO'] as RoleType[]).map(role => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving…' : 'Save Task'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
} 
import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Task, RoleType } from '@/types'
import { taskApi } from '@/lib/api'

interface EditTaskModalProps {
  open: boolean
  onClose: () => void
  task: Task | null
  onTaskUpdated?: (task: Task) => void
}

export default function EditTaskModal({ open, onClose, task, onTaskUpdated }: EditTaskModalProps) {
  const [description, setDescription] = useState('')
  const [assignedRole, setAssignedRole] = useState<RoleType>('CEO')
  const [status, setStatus] = useState<Task['status']>('pending')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (task) {
      setDescription(task.description)
      setAssignedRole(task.assigned_to_role)
      setStatus(task.status)
    }
  }, [task])

  if (!open || !task) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim()) return
    try {
      setLoading(true)
      const updated = await taskApi.update(task.id, {
        description,
        assigned_to_role: assignedRole,
        status,
      } as any)
      onTaskUpdated && onTaskUpdated(updated)
      onClose()
    } catch (err) {
      console.error('Failed to update task', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>Edit Task</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <Input value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Assign to</label>
              <select className="w-full border rounded px-3 py-2 text-sm" value={assignedRole} onChange={(e) => setAssignedRole(e.target.value as RoleType)}>
                {(['CEO', 'CTO', 'CMO'] as RoleType[]).map(role => <option key={role} value={role}>{role}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select className="w-full border rounded px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value as Task['status'])}>
                {(['pending','in_progress','completed'] as Task['status'][]).map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
              </select>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
              <Button type="submit" disabled={loading}>{loading ? 'Saving…' : 'Save'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
} 
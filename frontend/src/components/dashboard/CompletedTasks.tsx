import { useEffect, useState } from 'react'
import { taskApi } from '@/lib/api'
import { Task, RoleType } from '@/types'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Badge } from '../ui/badge'

interface CompletedTasksProps {
  userId: string
}

export default function CompletedTasks({ userId }: CompletedTasksProps) {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    const load = async () => {
      try {
        const t = await taskApi.getUserTasks(userId, 'completed')
        setTasks(t)
      } catch (err) {
        console.error('Failed to load completed tasks', err)
      }
    }
    load()
  }, [userId])

  return (
    <Card className="max-h-72 flex flex-col">
      <CardHeader>
        <CardTitle>Completed Tasks</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-3">
        {tasks.length === 0 && <p className="text-sm text-gray-500">No completed tasks yet.</p>}
        {tasks.map(task => (
          <div key={task.id} className="border rounded-md p-3">
            <div className="flex justify-between items-center">
              <p className="text-sm font-medium">{task.description}</p>
              <Badge>{task.assigned_to_role}</Badge>
            </div>
            {task.resources && task.resources.length > 0 && (
              <ul className="mt-2 text-xs list-disc list-inside space-y-1">
                {task.resources.map(res => (
                  <li key={res} className="text-blue-600 hover:underline cursor-pointer" onClick={() => window.open(`/api/files/raw?path=${encodeURIComponent(res)}`, '_blank')}>{res}</li>
                ))}
              </ul>
            )}
            <p className="text-xs text-gray-500 mt-1">Completed at {new Date(task.updated_at || task.created_at).toLocaleString()}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
} 
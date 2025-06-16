'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { taskApi } from '@/lib/api'
import { Task, User, RoleType } from '@/types'
import { getRoleColor, formatDate } from '@/lib/utils'
import { CheckCircle, Circle, Clock, Plus, Pencil, Trash2 } from 'lucide-react'
import AddTaskModal from './AddTaskModal'
import EditTaskModal from './EditTaskModal'

interface TaskListProps {
  user: User
}

export default function TaskList({ user }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [showAdd, setShowAdd] = useState(false)
  const [editTask, setEditTask] = useState<Task | null>(null)

  useEffect(() => {
    loadTasks()
    const handler = (e: any) => {
      if (e.detail) {
        setTasks(prev => [e.detail, ...prev])
      }
    }
    window.addEventListener('task_created', handler)
    return () => window.removeEventListener('task_created', handler)
  }, [user.id])

  const loadTasks = async () => {
    try {
      const userTasks = await taskApi.getUserTasks(user.id)
      setTasks(userTasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTaskCreated = (task: Task) => {
    setTasks(prev => [task, ...prev])
  }

  const updateTaskStatus = async (taskId: string, status: Task['status']) => {
    try {
      const updatedTask = await taskApi.update(taskId, { status })
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ))
    } catch (error) {
      console.error('Failed to update task:', error)
    }
  }

  const handleDelete = async (taskId: string) => {
    if (!confirm('Delete this task?')) return
    try {
      await taskApi.delete(taskId)
      setTasks(prev => prev.filter(t => t.id !== taskId))
    } catch (err) {
      console.error('Delete failed', err)
    }
  }

  const handleTaskUpdated = (updated: Task) => {
    setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)))
  }

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true
    return task.status === filter
  })

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-600" />
      default:
        return <Circle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className="max-h-[22rem] flex flex-col">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Tasks</CardTitle>
            <Button size="sm" variant="outline" onClick={() => setShowAdd(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Task
            </Button>
          </div>
          
          {/* Filter Buttons */}
          <div className="flex gap-2 mt-4">
            {(['all', 'pending', 'in_progress', 'completed'] as const).map((status) => (
              <Button
                key={status}
                variant={filter === status ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(status)}
              >
                {status === 'all' ? 'All' : status.replace('_', ' ')}
                <span className="ml-1 text-xs">
                  ({status === 'all' ? tasks.length : tasks.filter(t => t.status === status).length})
                </span>
              </Button>
            ))}
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 overflow-y-auto">
          {filteredTasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Circle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>No tasks found</p>
              <p className="text-sm mt-2">
                {filter === 'all' 
                  ? 'Your AI agents will create tasks to help you build your startup'
                  : `No ${filter.replace('_', ' ')} tasks`
                }
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className="p-4 border rounded-lg hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1">
                      <button
                        onClick={() => {
                          const nextStatus = task.status === 'pending' 
                            ? 'in_progress' 
                            : task.status === 'in_progress' 
                            ? 'completed' 
                            : 'pending'
                          updateTaskStatus(task.id, nextStatus)
                        }}
                        className="mt-1"
                      >
                        {getStatusIcon(task.status)}
                      </button>
                      
                      <div className="flex-1">
                        <p className={`text-sm ${task.status === 'completed' ? 'line-through text-gray-500' : ''}`}>
                          {task.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getRoleColor(task.assigned_to_role)}`}>
                            {task.assigned_to_role}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(task.status)}`}>
                            {task.status.replace('_', ' ')}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatDate(task.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2 ml-2">
                      <Button size="icon" variant="ghost" onClick={() => setEditTask(task)}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button size="icon" variant="ghost" onClick={() => handleDelete(task.id)}>
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      {showAdd && (
        <AddTaskModal
          open={showAdd}
          onClose={() => setShowAdd(false)}
          user={user}
          onTaskCreated={handleTaskCreated}
        />
      )}
      {editTask && (
        <EditTaskModal
          open={!!editTask}
          task={editTask}
          onClose={() => setEditTask(null)}
          onTaskUpdated={handleTaskUpdated}
        />
      )}
    </>
  )
} 
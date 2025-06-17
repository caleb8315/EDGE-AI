import { useEffect, useState } from 'react'
import { taskApi, filesApi } from '@/lib/api'
import { Task } from '@/types'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Pencil, Trash2, Download, FileText, Eye } from 'lucide-react'
import EditTaskModal from './EditTaskModal'
import FileViewerModal from './FileViewerModal'

interface TasksAndResourcesProps {
  userId: string
}

export default function TasksAndResources({ userId }: TasksAndResourcesProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [editTask, setEditTask] = useState<Task | null>(null)
  const [allFiles, setAllFiles] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedFile, setSelectedFile] = useState<{ path: string; content: string } | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        
        // Load completed tasks
        const completedTasks = await taskApi.getUserTasks(userId, 'completed')
        setTasks(completedTasks)
        
        // Load all workspace files
        const files = await filesApi.list()
        setAllFiles(files)
        
      } catch (err) {
        console.error('Failed to load tasks and files', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this task?')) return
    try {
      await taskApi.delete(id)
      setTasks(prev => prev.filter(t => t.id !== id))
    } catch (e) {
      console.error(e)
    }
  }

  const handleTaskUpdated = (updated: Task) => {
    setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)))
  }

  const handleViewFile = async (filePath: string) => {
    try {
      // For now, we only support viewing text-based files.
      const textExtensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml', '.sql']
      const extension = filePath.substring(filePath.lastIndexOf('.'))
      
      if (!textExtensions.includes(extension)) {
        alert("This file type cannot be viewed directly. Please download it instead.")
        return
      }

      const content = await filesApi.read(filePath)
      setSelectedFile({ path: filePath, content })
    } catch (e) {
      console.error('Failed to read file:', e)
      alert('Failed to read file for viewing.')
    }
  }

  const handleDownloadFile = async (filePath: string) => {
    try {
      const content = await filesApi.read(filePath)
      const blob = new Blob([content], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filePath.split('/').pop() || 'download.txt'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Failed to download file:', e)
      alert('Failed to download file')
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-gray-500">Loading...</p>
        </CardContent>
      </Card>
    )
  }

  // Get task files (files that are linked to completed tasks)
  const taskFiles = new Set<string>()
  tasks.forEach(task => {
    task.resources?.forEach(resource => taskFiles.add(resource))
  })

  // Get other workspace files (not linked to tasks)
  const otherFiles = allFiles.filter(file => !taskFiles.has(file))

  return (
    <>
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>Tasks & Resources</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 space-y-6">
          
          {/* Completed Tasks Section */}
          <div>
            <h3 className="font-semibold text-lg mb-3">Completed Tasks</h3>
            {tasks.length === 0 ? (
              <p className="text-sm text-gray-500">No completed tasks yet.</p>
            ) : (
              <div className="space-y-3">
                {tasks.map(task => (
                  <div key={task.id} className="border rounded-md p-3 bg-green-50">
                    <div className="flex justify-between items-start gap-2 mb-2">
                      <p className="text-sm font-medium flex-1">{task.description}</p>
                      <div className="flex items-center gap-1">
                        <Badge variant="secondary">{task.assigned_to_role}</Badge>
                        <Button size="icon" variant="ghost" onClick={() => setEditTask(task)}>
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button size="icon" variant="ghost" onClick={() => handleDelete(task.id)}>
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
                      </div>
                    </div>
                    
                    {/* Task Resources */}
                    {task.resources && task.resources.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-gray-600 mb-1">Generated Files:</p>
                        <div className="flex flex-wrap gap-2">
                          {task.resources.map(resource => (
                            <div key={resource} className="flex items-center gap-1">
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 text-xs pr-2"
                                onClick={() => handleViewFile(resource)}
                              >
                                <FileText className="w-3 h-3 mr-1" />
                                {resource.split('/').pop()}
                                <Eye className="w-3 h-3 ml-2" />
                              </Button>
                              <Button
                                size="icon"
                                variant="ghost"
                                className="h-8 w-8"
                                onClick={() => handleDownloadFile(resource)}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <p className="text-xs text-gray-500 mt-2">
                      Completed at {new Date(task.updated_at || task.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Other Workspace Files Section */}
          {otherFiles.length > 0 && (
            <div>
              <h3 className="font-semibold text-lg mb-3">Other Workspace Files</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {otherFiles.map(file => (
                  <div key={file} className="flex items-center gap-1">
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-10 justify-between flex-1 truncate"
                      onClick={() => handleViewFile(file)}
                    >
                      <span className="truncate text-left">{file.split('/').pop()}</span>
                      <Eye className="w-4 h-4 ml-2 flex-shrink-0" />
                    </Button>
                     <Button
                        size="icon"
                        variant="ghost"
                        className="h-10 w-10"
                        onClick={() => handleDownloadFile(file)}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {editTask && (
        <EditTaskModal 
          open={!!editTask} 
          task={editTask} 
          onClose={() => setEditTask(null)} 
          onTaskUpdated={handleTaskUpdated} 
        />
      )}

      {selectedFile && (
        <FileViewerModal
          open={!!selectedFile}
          onClose={() => setSelectedFile(null)}
          filePath={selectedFile.path}
          fileContent={selectedFile.content}
        />
      )}
    </>
  )
} 
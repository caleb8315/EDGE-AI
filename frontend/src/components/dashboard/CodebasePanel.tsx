import { useEffect, useState, useRef } from 'react'
import { filesApi, companyApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Plus, Folder, Upload, FileText, Code } from 'lucide-react'

interface CodebasePanelProps {
  userId?: string
}

export default function CodebasePanel({ userId }: CodebasePanelProps) {
  const [directories, setDirectories] = useState<string[]>([])
  const [newDir, setNewDir] = useState<string>('')
  const [selectedDir, setSelectedDir] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [codebaseFiles, setCodebaseFiles] = useState<string[]>([])
  const [aiSummary, setAiSummary] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const folderInputRef = useRef<HTMLInputElement>(null)

  const refresh = async (abortController?: AbortController) => {
    try {
      const paths = await filesApi.list(abortController?.signal)
      const dirs = Array.from(
        new Set(
          paths
            .map(p => p.includes('/') ? p.split('/')[0] : '')
            .filter(Boolean)
        )
      )
      setDirectories(dirs.sort())
      
      // Also refresh codebase files from company
      if (userId) {
        const files = await companyApi.getCodebaseFiles(userId)
        setCodebaseFiles(files)
      }

      // Get AI accessibility summary
      try {
        const summary = await filesApi.summary()
        setAiSummary(summary)
    } catch (e) {
        console.error('Failed to load AI summary', e)
      }
    } catch (e: any) {
      // Only log error if it's not an abort/cancel error
      if (e.name !== 'AbortError' && e.name !== 'CanceledError' && e.code !== 'ERR_CANCELED') {
      console.error('Failed to load directories', e)
      }
    }
  }

  useEffect(() => {
    const abortController = new AbortController()
    refresh(abortController)
    
    return () => {
      abortController.abort()
    }
  }, [userId])

  const handleCreate = async () => {
    if (!newDir.trim()) return
    try {
      await filesApi.mkdir(newDir.trim())
      setNewDir('')
      refresh()
    } catch (e: any) {
      console.error('Directory creation error:', e)
      alert(`Failed to create directory: ${e.response?.data?.detail || e.message}`)
    }
  }

  const handleFileSelect = () => {
    fileInputRef.current?.click()
  }

  const handleFolderSelect = () => {
    folderInputRef.current?.click()
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    try {
      console.log('Uploading files:', files.length, 'to directory:', selectedDir, 'userId:', userId)
      const result = await filesApi.upload(files, selectedDir)
      alert(`Successfully uploaded ${result.count} files`)
      refresh()
    } catch (e: any) {
      console.error('File upload error:', e)
      alert(`Failed to upload files: ${e.response?.data?.detail || e.message}`)
    } finally {
      setUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      if (folderInputRef.current) {
        folderInputRef.current.value = ''
      }
    }
  }

  return (
    <Card className="max-h-96 flex flex-col">
      <CardHeader>
        <CardTitle>Project Directories</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4">
        {/* Create Directory */}
        <div className="flex gap-2">
          <Input
            placeholder="New directory name"
            value={newDir}
            onChange={e => setNewDir(e.target.value)}
          />
          <Button onClick={handleCreate} variant="outline" size="sm">
            <Plus className="w-4 h-4 mr-1" />Add
          </Button>
        </div>

        {/* Upload Files */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <select
              value={selectedDir}
              onChange={e => setSelectedDir(e.target.value)}
              className="flex-1 h-9 rounded-md border border-input bg-background px-3 py-1 text-sm"
            >
              <option value="">Root directory</option>
              {directories.map(dir => (
                <option key={dir} value={dir}>{dir}</option>
              ))}
            </select>
            <Button 
              onClick={handleFileSelect} 
              variant="outline" 
              size="sm"
              disabled={uploading}
            >
              <FileText className="w-4 h-4 mr-1" />
              Files
            </Button>
            <Button 
              onClick={handleFolderSelect} 
              variant="outline" 
              size="sm"
              disabled={uploading}
            >
              <Folder className="w-4 h-4 mr-1" />
              Folder
            </Button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileUpload}
            className="hidden"
            accept=".py,.js,.ts,.tsx,.jsx,.html,.css,.md,.txt,.json,.yaml,.yml"
          />
          <input
            ref={folderInputRef}
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            {...({ webkitdirectory: "" } as any)}
            multiple
          />
          <p className="text-xs text-gray-500">
            Select directory and upload files or entire folders
          </p>
          {uploading && (
            <div className="flex items-center gap-2 text-xs text-blue-600 p-2 bg-blue-50 rounded-md">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
              Uploading files... This may take up to 60 seconds for large files.
            </div>
          )}
        </div>

        {/* Directory List */}
        <ul className="space-y-1">
          {directories.map(dir => (
            <li key={dir} className="flex items-center gap-2 text-sm">
              <Folder className="w-4 h-4 text-yellow-500" />
              {dir}
            </li>
          ))}
          {directories.length === 0 && <p className="text-xs text-gray-500">No directories yet</p>}
        </ul>

        {/* AI Accessibility Status */}
        {aiSummary && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              🤖 AI Assistant Access
            </h4>
            <div className="text-xs text-gray-600 space-y-1">
              <p>✅ {aiSummary.ai_accessible_count} files readable by AI agents</p>
              <p>📁 {aiSummary.total_files} total files uploaded</p>
              {aiSummary.ai_accessible_count > 0 && (
                <div className="mt-2 p-2 bg-green-50 rounded-md">
                  <p className="text-green-800 font-medium">🎯 Your AI team can now:</p>
                  <ul className="text-green-700 mt-1 space-y-1">
                    <li>• CTO: Analyze your codebase & architecture</li>
                    <li>• CMO: Review docs & marketing materials</li>
                    <li>• CEO: Access business documents & plans</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Codebase Files from Company */}
        {codebaseFiles.length > 0 && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <Code className="w-4 h-4" />
              Tracked Codebase Files ({codebaseFiles.length})
            </h4>
            <div className="max-h-32 overflow-y-auto">
              <ul className="space-y-1">
                {codebaseFiles.slice(0, 10).map(file => (
                  <li key={file} className="text-xs text-gray-600 truncate">
                    {file}
                  </li>
                ))}
                {codebaseFiles.length > 10 && (
                  <li className="text-xs text-gray-500 italic">
                    ...and {codebaseFiles.length - 10} more files
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 
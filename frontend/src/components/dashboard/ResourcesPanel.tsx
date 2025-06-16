import { useEffect, useState } from 'react'
import { filesApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import dynamic from 'next/dynamic'
import { Input } from '../ui/input'
import { Download } from 'lucide-react'

interface ResourcesPanelProps {
  onSelect?: (path: string) => void
}

export default function ResourcesPanel({ onSelect }: ResourcesPanelProps) {
  const [files, setFiles] = useState<string[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [content, setContent] = useState<string>('')
  const [filter, setFilter] = useState<string>('')

  useEffect(() => {
    const load = async () => {
      try {
        const list = await filesApi.list()
        setFiles(list)
      } catch (e) {
        console.error('Failed to list files', e)
      }
    }
    load()
  }, [])

  const handleSelect = async (path: string) => {
    setSelected(path)
    if (onSelect) onSelect(path)
    try {
      const text = await filesApi.read(path)
      setContent(text)
    } catch (e) {
      setContent('⚠️ Unable to preview (binary or large file).')
    }
  }

  const filteredFiles = files.filter(f => f.toLowerCase().includes(filter.toLowerCase()))

  // Build simple grouping by first directory segment
  const groups = filteredFiles.reduce<Record<string, string[]>>((acc, file) => {
    const [dir, ...rest] = file.split('/')
    const key = rest.length ? dir : '[root]'
    if (!acc[key]) acc[key] = []
    acc[key].push(file)
    return acc
  }, {})

  return (
    <Card className="max-h-96 flex flex-col">
      <CardHeader>
        <CardTitle>Workspace Resources</CardTitle>
        <Input
          placeholder="Search files..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="mt-2"
        />
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto">
        <div className="mb-4 space-y-2">
          {Object.entries(groups).map(([dir, files]) => (
            <details key={dir} open className="border rounded-md p-2">
              <summary className="cursor-pointer select-none font-medium text-sm mb-1">{dir}</summary>
              <ul className="pl-4 space-y-1 mt-1">
                {files.map(f => (
                  <li key={f}>
                    <Button
                      variant={f === selected ? 'secondary' : 'ghost'}
                      size="sm"
                      className="w-full justify-between"
                      onClick={() => handleSelect(f)}
                    >
                      <span className="truncate text-left">{f.split('/').slice(1).join('/') || f}</span>
                      <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/files/raw?path=${encodeURIComponent(f)}`} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>
                        <Download className="w-4 h-4 opacity-70 hover:opacity-100" />
                      </a>
                    </Button>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
        {selected && (
          <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-3 rounded-md overflow-x-auto max-h-64">
            {content}
          </pre>
        )}
      </CardContent>
    </Card>
  )
} 
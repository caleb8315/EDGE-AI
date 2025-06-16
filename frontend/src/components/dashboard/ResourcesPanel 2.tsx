import { useEffect, useState } from 'react'
import { filesApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import dynamic from 'next/dynamic'

interface ResourcesPanelProps {
  onSelect?: (path: string) => void
}

export default function ResourcesPanel({ onSelect }: ResourcesPanelProps) {
  const [files, setFiles] = useState<string[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [content, setContent] = useState<string>('')

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

  return (
    <Card className="max-h-72 flex flex-col">
      <CardHeader>
        <CardTitle>Workspace Resources</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto">
        <ul className="mb-4 space-y-1">
          {files.map(f => (
            <li key={f}>
              <Button variant={f === selected ? 'secondary' : 'ghost'} size="sm" className="w-full justify-start" onClick={() => handleSelect(f)}>
                {f}
              </Button>
            </li>
          ))}
        </ul>
        {selected && (
          <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-3 rounded-md overflow-x-auto max-h-64">
            {content}
          </pre>
        )}
      </CardContent>
    </Card>
  )
} 
import { Button } from '../ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog'
import { Download, X } from 'lucide-react'

interface FileViewerModalProps {
  open: boolean
  onClose: () => void
  filePath: string
  fileContent: string
}

export default function FileViewerModal({ open, onClose, filePath, fileContent }: FileViewerModalProps) {
  
  const handleDownload = () => {
    const blob = new Blob([fileContent], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filePath.split('/').pop() || 'download.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="truncate">{filePath}</DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-y-auto bg-gray-900 text-white p-4 rounded-md font-mono text-sm">
          <pre><code>{fileContent}</code></pre>
        </div>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={onClose}>
            <X className="w-4 h-4 mr-2" />
            Close
          </Button>
          <Button onClick={handleDownload}>
            <Download className="w-4 h-4 mr-2" />
            Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 
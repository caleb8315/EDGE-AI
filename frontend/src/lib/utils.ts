import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function getRoleColor(role: string) {
  switch (role) {
    case 'CEO':
      return 'bg-purple-100 text-purple-800 border-purple-200'
    case 'CTO':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'CMO':
      return 'bg-green-100 text-green-800 border-green-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

export function getRoleDescription(role: string) {
  switch (role) {
    case 'CEO':
      return 'Vision, strategy, and financial decisions'
    case 'CTO':
      return 'Technical architecture and MVP development'
    case 'CMO':
      return 'Marketing strategy and growth'
    default:
      return ''
  }
} 
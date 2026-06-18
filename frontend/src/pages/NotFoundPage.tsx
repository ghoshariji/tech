import { useNavigate } from 'react-router-dom'

export default function NotFoundPage() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-8xl font-bold text-muted-foreground">404</h1>
        <h2 className="text-2xl font-bold mt-4">Page not found</h2>
        <p className="text-muted-foreground mt-2">The page you're looking for doesn't exist.</p>
        <button onClick={() => navigate('/dashboard')} className="mt-6 px-6 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90">
          Go to Dashboard
        </button>
      </div>
    </div>
  )
}

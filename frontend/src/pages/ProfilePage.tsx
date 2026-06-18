import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { Loader2, User, Lock } from 'lucide-react'
import toast from 'react-hot-toast'
import { userService } from '@/services/user.service'
import { useAuthStore } from '@/store/authStore'
import { PageHeader } from '@/components/common/PageHeader'
import { formatDate, getApiError, getRoleColor } from '@/lib/utils'

const pwSchema = z.object({
  current_password: z.string().min(1, 'Required'),
  new_password: z.string().min(8).regex(/[A-Z]/).regex(/[a-z]/).regex(/[0-9]/).regex(/[@$!%*?&_#^()\-+=]/),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, { message: "Passwords don't match", path: ['confirm_password'] })

type PwForm = z.infer<typeof pwSchema>

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PwForm>({
    resolver: zodResolver(pwSchema),
  })

  const mutation = useMutation({
    mutationFn: (data: PwForm) => userService.changePassword(data.current_password, data.new_password),
    onSuccess: () => { toast.success('Password changed successfully'); reset() },
    onError: (err) => toast.error(getApiError(err)),
  })

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Profile" description="Manage your account" />

      {/* User Info */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="h-16 w-16 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-2xl font-bold">
            {user?.full_name?.charAt(0)?.toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold">{user?.full_name}</h2>
            <p className="text-muted-foreground">{user?.email}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block ${getRoleColor(user?.role || '')}`}>{user?.role}</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm pt-4 border-t border-border">
          <div>
            <p className="text-muted-foreground text-xs mb-0.5">Account Status</p>
            <p className="font-medium">{user?.is_active ? '✅ Active' : '❌ Inactive'}</p>
          </div>
          <div>
            <p className="text-muted-foreground text-xs mb-0.5">Email Verified</p>
            <p className="font-medium">{user?.is_verified ? '✅ Verified' : '⚠️ Unverified'}</p>
          </div>
        </div>
      </div>

      {/* Change Password */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2"><Lock className="h-4 w-4" /> Change Password</h3>
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Current Password</label>
            <input {...register('current_password')} type="password" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            {errors.current_password && <p className="text-xs text-destructive mt-1">{errors.current_password.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">New Password</label>
            <input {...register('new_password')} type="password" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            {errors.new_password && <p className="text-xs text-destructive mt-1">Must be 8+ chars with uppercase, lowercase, number & special char</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Confirm New Password</label>
            <input {...register('confirm_password')} type="password" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            {errors.confirm_password && <p className="text-xs text-destructive mt-1">{errors.confirm_password.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="px-6 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-60 flex items-center gap-2">
            {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
            Update Password
          </button>
        </form>
      </div>
    </div>
  )
}

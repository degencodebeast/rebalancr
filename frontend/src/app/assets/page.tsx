'use client'

import DashboardLayout from '@/components/Layout/DashboardLayout'

export default function Assets() {
  return (
    <DashboardLayout>
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Assets</h1>

        {/* Assets content goes here */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-2">Your Assets</h2>
          <p>Your assets will be listed here</p>
        </div>
      </div>
    </DashboardLayout>
  )
}

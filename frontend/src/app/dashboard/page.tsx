export default function DashboardPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl mb-4">Portfolio Summary</h2>
          {/* Portfolio components will go here */}
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl mb-4">Market Overview</h2>
          {/* Market data will go here */}
        </div>
      </div>
    </div>
  );
}

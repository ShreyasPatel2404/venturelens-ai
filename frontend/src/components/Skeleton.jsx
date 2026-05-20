// frontend/src/components/Skeleton.jsx
// Reusable shimmer skeleton blocks

function Shimmer({ className = "" }) {
  return (
    <div className={`bg-gray-800 rounded animate-pulse ${className}`} />
  );
}

export function HistoryItemSkeleton() {
  return (
    <div className="border-b border-gray-800/60 px-4 py-3 space-y-2">
      <div className="flex items-center justify-between">
        <Shimmer className="h-3 w-32" />
        <Shimmer className="h-3 w-8" />
      </div>
      <Shimmer className="h-2 w-24" />
    </div>
  );
}

export function ResultsSkeleton() {
  return (
    <div className="space-y-6 animate-pulse" style={{ fontFamily: "'DM Mono', monospace" }}>
      {/* Header */}
      <div className="space-y-2">
        <Shimmer className="h-3 w-32" />
        <Shimmer className="h-8 w-48" />
        <Shimmer className="h-3 w-24" />
      </div>
      {/* Score card */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <div className="grid grid-cols-5 gap-6">
          <div className="col-span-2 flex flex-col items-center gap-3">
            <Shimmer className="w-32 h-32 rounded-full" />
            <Shimmer className="h-2 w-20" />
          </div>
          <div className="col-span-3 space-y-4">
            {[...Array(5)].map((_,i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between">
                  <Shimmer className="h-2 w-32" />
                  <Shimmer className="h-2 w-6" />
                </div>
                <Shimmer className="h-1.5 w-full" />
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Summary */}
      <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 space-y-2">
        <Shimmer className="h-2 w-32 mb-3" />
        <Shimmer className="h-3 w-full" />
        <Shimmer className="h-3 w-5/6" />
        <Shimmer className="h-3 w-4/6" />
      </div>
    </div>
  );
}
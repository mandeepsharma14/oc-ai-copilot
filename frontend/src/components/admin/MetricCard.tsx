interface MetricCardProps {
  label:  string;
  value:  string | number;
  delta?: string;
  good?:  boolean;
}

export function MetricCard({ label, value, delta, good = true }: MetricCardProps) {
  return (
    <div className="bg-gray-50 rounded-lg px-3 py-2.5">
      <div className="text-[10px] text-gray-500 mb-1">{label}</div>
      <div className="text-lg font-medium text-gray-900">{value}</div>
      {delta && (
        <div className={`text-[9px] mt-0.5 ${good ? "text-green-700" : "text-red-600"}`}>
          {delta}
        </div>
      )}
    </div>
  );
}

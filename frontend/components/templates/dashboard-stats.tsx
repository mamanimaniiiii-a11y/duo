type StatItem = {
  label: string;
  value: string;
  colorClass: string;
};

type DashboardStatsProps = {
  items: StatItem[];
};

export function DashboardStats({ items }: DashboardStatsProps) {
  return (
    <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className={`rounded-xl px-5 py-4 text-white ${item.colorClass}`}
        >
          <p className="text-sm text-white/80">{item.label}</p>
          <p className="mt-1 text-2xl font-semibold">{item.value}</p>
        </div>
      ))}
    </div>
  );
}

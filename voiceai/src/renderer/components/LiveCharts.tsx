import { useState, useEffect, useRef } from 'react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
);

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string | string[];
    borderColor?: string;
    fill?: boolean;
  }[];
}

interface LiveChartProps {
  type: 'line' | 'bar' | 'pie' | 'doughnut';
  data: ChartData;
  title?: string;
  height?: number;
  live?: boolean;
  onUpdate?: (data: ChartData) => void;
}

const chartColors = [
  'rgba(0, 212, 255, 0.8)',   // Cyan
  'rgba(0, 255, 136, 0.8)',  // Green
  'rgba(255, 68, 68, 0.8)',  // Red
  'rgba(255, 165, 0, 0.8)',   // Orange
  'rgba(138, 43, 226, 0.8)',  // Purple
  'rgba(255, 215, 0, 0.8)',   // Gold
  'rgba(0, 255, 255, 0.8)',   // Cyan
  'rgba(255, 0, 255, 0.8)',   // Magenta
];

const baseOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
      labels: { color: '#e2e8f0', font: { size: 12 } }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#00d4ff',
      bodyColor: '#fff',
      borderColor: '#00d4ff',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255, 255, 255, 0.1)' },
      ticks: { color: '#94a3b8' }
    },
    y: {
      grid: { color: 'rgba(255, 255, 255, 0.1)' },
      ticks: { color: '#94a3b8' }
    }
  },
  animation: {
    duration: 800,
    easing: 'easeOutQuart' as const
  }
};

export default function LiveChart({ type, data, title, height = 250, live = false, onUpdate }: LiveChartProps) {
  const chartRef = useRef<any>(null);
  const [chartData, setChartData] = useState<ChartData>(data);

  useEffect(() => {
    setChartData(data);
  }, [data]);

  useEffect(() => {
    if (!live) return;

    const interval = setInterval(() => {
      if (chartRef.current) {
        chartRef.current.update('none');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [live]);

  const renderChart = () => {
    const options = {
      ...baseOptions,
      plugins: {
        ...baseOptions.plugins,
        title: title ? {
          display: true,
          text: title,
          color: '#00d4ff',
          font: { size: 16, weight: 'bold' as const },
          padding: 20
        } : undefined
      }
    };

    switch (type) {
      case 'line':
        return <Line ref={chartRef} data={chartData} options={options} />;
      case 'bar':
        return <Bar ref={chartRef} data={chartData} options={options} />;
      case 'pie':
        return <Pie ref={chartRef} data={chartData} options={{
          ...baseOptions,
          plugins: {
            ...baseOptions.plugins,
            title: title ? {
              display: true,
              text: title,
              color: '#00d4ff',
              font: { size: 16, weight: 'bold' as const }
            } : undefined
          }
        }} />;
      case 'doughnut':
        return <Doughnut ref={chartRef} data={chartData} options={options} />;
      default:
        return <Line ref={chartRef} data={chartData} options={options} />;
    }
  };

  return (
    <div className="bg-surface/50 rounded-xl border border-border p-4" style={{ height }}>
      <div ref={chartRef} style={{ height: height - 60 }}>
        {renderChart()}
      </div>
      {live && (
        <div className="flex items-center gap-2 mt-2 text-xs text-primary">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
          <span>LIVE</span>
        </div>
      )}
    </div>
  );
}

export function ThreatDistribution({ data }: { data: { type: string; count: number }[] }) {
  const chartData: ChartData = {
    labels: data.map(d => d.type),
    datasets: [{
      label: 'Threats',
      data: data.map(d => d.count),
      backgroundColor: data.map((_, i) => chartColors[i % chartColors.length]),
      borderColor: '#1e293b',
      borderWidth: 2
    }]
  };

  return <LiveChart type="doughnut" data={chartData} title="Threat Distribution" height={280} />;
}

export function SecurityTrend({ data }: { data: { day: string; score: number }[] }) {
  const chartData: ChartData = {
    labels: data.map(d => d.day),
    datasets: [{
      label: 'Security Score',
      data: data.map(d => d.score),
      borderColor: '#00ff88',
      backgroundColor: 'rgba(0, 255, 136, 0.2)',
      fill: true,
      tension: 0.4
    }]
  };

  return <LiveChart type="line" data={chartData} title="Security Score Trend" height={280} live />;
}

export function ModuleUsage({ data }: { data: { module: string; calls: number }[] }) {
  const chartData: ChartData = {
    labels: data.map(d => d.module),
    datasets: [{
      label: 'API Calls',
      data: data.map(d => d.calls),
      backgroundColor: chartColors.slice(0, data.length),
      borderWidth: 0
    }]
  };

  return <LiveChart type="bar" data={chartData} title="Module Usage" height={280} />;
}

export function SystemMetrics({ cpu, memory, disk }: { cpu: number; memory: number; disk: number }) {
  const data = {
    labels: ['CPU', 'Memory', 'Disk'],
    datasets: [{
      label: 'Usage %',
      data: [cpu, memory, disk],
      backgroundColor: [
        cpu > 80 ? 'rgba(255, 68, 68, 0.8)' : 'rgba(0, 212, 255, 0.8)',
        memory > 80 ? 'rgba(255, 68, 68, 0.8)' : 'rgba(0, 255, 136, 0.8)',
        disk > 80 ? 'rgba(255, 68, 68, 0.8)' : 'rgba(255, 165, 0, 0.8)'
      ],
      borderWidth: 0
    }]
  };

  return <LiveChart type="bar" data={data} title="System Resources" height={200} />;
}

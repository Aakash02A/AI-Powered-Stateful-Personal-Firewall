import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { DataTable, type Column } from '../components/DataTable';
import { apiClient } from '../api/client';

export interface ConnectionData {
  id?: number;
  src_ip: string;
  src_port: number;
  dst_ip: string;
  dst_port: number;
  protocol: string;
  state: string;
  creation_time: string;
  duration: number;
  bytes_in: number;
  bytes_out: number;
}

export function Connections() {
  const { data: response, isLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.get('/connections?limit=500').then(res => res.data),
    refetchInterval: 5000,
  });

  const connections: ConnectionData[] = response?.data || [];

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const columns: Column<ConnectionData>[] = [
    {
      key: 'creation_time',
      header: 'Start Time',
      sortable: true,
      render: (row) => format(new Date(row.creation_time), 'HH:mm:ss')
    },
    {
      key: 'src_ip',
      header: 'Source',
      sortable: true,
      render: (row) => <span className="font-mono text-slate-300">{row.src_ip}:{row.src_port}</span>
    },
    {
      key: 'dst_ip',
      header: 'Destination',
      sortable: true,
      render: (row) => <span className="font-mono text-slate-300">{row.dst_ip}:{row.dst_port}</span>
    },
    { 
      key: 'protocol', 
      header: 'Protocol', 
      sortable: true,
      render: (row) => <span className="text-primary font-medium">{row.protocol}</span>
    },
    { 
      key: 'state', 
      header: 'State', 
      sortable: true,
      render: (row) => (
        <span className={`px-2 py-1 rounded text-[10px] uppercase font-bold tracking-wider ${
          row.state === 'ESTABLISHED' ? 'bg-success/20 text-success' : 
          row.state === 'CLOSED' ? 'bg-slate-800 text-slate-400' : 
          'bg-warning/20 text-warning'
        }`}>
          {row.state}
        </span>
      )
    },
    { 
      key: 'duration', 
      header: 'Duration', 
      sortable: true,
      render: (row) => `${row.duration.toFixed(1)}s`
    },
    { 
      key: 'bytes_out', 
      header: 'Data (Out/In)', 
      sortable: true,
      render: (row) => (
        <div className="flex flex-col text-xs space-y-1">
          <span className="text-slate-300">↑ {formatBytes(row.bytes_out)}</span>
          <span className="text-slate-500">↓ {formatBytes(row.bytes_in)}</span>
        </div>
      )
    },
  ];

  return (
    <div className="h-full flex flex-col space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Active Connections</h1>
          <p className="text-sm text-slate-400 mt-1">Live view of network flows tracked by the stateful firewall.</p>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <DataTable 
          data={connections} 
          columns={columns} 
          isLoading={isLoading} 
          searchPlaceholder="Search IPs, ports, or protocols..."
        />
      </div>
    </div>
  );
}

import { useState, useMemo, useRef } from 'react';
import { ChevronDown, ChevronUp, Search } from 'lucide-react';
import { useVirtualizer } from '@tanstack/react-virtual';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  isLoading?: boolean;
}

export function DataTable<T extends Record<string, any>>({ 
  data, 
  columns, 
  searchPlaceholder = 'Search...',
  onSearch,
  isLoading 
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDesc, setSortDesc] = useState(false);
  const [localSearch, setLocalSearch] = useState('');

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDesc(!sortDesc);
    } else {
      setSortKey(key);
      setSortDesc(false);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalSearch(e.target.value);
    if (onSearch) {
      onSearch(e.target.value);
    }
  };

  // Local sorting and filtering if no external search is provided
  const processedData = useMemo(() => {
    let result = [...data];

    if (!onSearch && localSearch) {
      const lowerQuery = localSearch.toLowerCase();
      result = result.filter(item => 
        Object.values(item).some(val => 
          String(val).toLowerCase().includes(lowerQuery)
        )
      );
    }

    if (sortKey) {
      result.sort((a, b) => {
        const valA = a[sortKey];
        const valB = b[sortKey];
        if (valA < valB) return sortDesc ? 1 : -1;
        if (valA > valB) return sortDesc ? -1 : 1;
        return 0;
      });
    }

    return result;
  }, [data, sortKey, sortDesc, localSearch, onSearch]);

  const parentRef = useRef<HTMLDivElement>(null);
  const rowVirtualizer = useVirtualizer({
    count: processedData.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 53, // Approx height of tr
    overscan: 5,
  });

  return (
    <div className="glass-panel flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/30">
        <div className="relative w-64">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-slate-500" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-slate-700 rounded-md leading-5 bg-slate-900/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm transition-colors"
            placeholder={searchPlaceholder}
            value={localSearch}
            onChange={handleSearchChange}
          />
        </div>
      </div>

      <div ref={parentRef} className="flex-1 overflow-auto relative">
        <table className="min-w-full divide-y divide-slate-700/50 text-sm table-fixed">
          <thead className="bg-slate-900/80 sticky top-0 z-20 backdrop-blur-sm block">
            <tr className="flex w-full">
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  style={{ width: col.width || `${100 / columns.length}%` }}
                  className={`px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider ${col.sortable ? 'cursor-pointer hover:bg-slate-800/50' : ''}`}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{col.header}</span>
                    {col.sortable && sortKey === col.key && (
                      sortDesc ? <ChevronDown className="w-3 h-3 text-primary" /> : <ChevronUp className="w-3 h-3 text-primary" />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody 
            className="divide-y divide-slate-700/50 bg-transparent block relative"
            style={{ height: `${rowVirtualizer.getTotalSize()}px` }}
          >
            {isLoading ? (
              <tr className="flex w-full relative">
                <td className="px-6 py-8 text-center text-slate-500 w-full">
                  <div className="animate-pulse flex flex-col items-center justify-center space-y-2">
                    <div className="h-4 bg-slate-700 rounded w-1/4"></div>
                    <div className="h-4 bg-slate-700 rounded w-1/2"></div>
                  </div>
                </td>
              </tr>
            ) : processedData.length === 0 ? (
              <tr className="flex w-full relative">
                <td className="px-6 py-8 text-center text-slate-500 w-full">
                  No data found
                </td>
              </tr>
            ) : (
              rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const row = processedData[virtualRow.index];
                return (
                  <tr 
                    key={virtualRow.index} 
                    className="hover:bg-slate-800/30 transition-colors flex w-full absolute"
                    style={{
                      height: `${virtualRow.size}px`,
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                  >
                    {columns.map((col) => (
                      <td 
                        key={col.key} 
                        style={{ width: col.width || `${100 / columns.length}%` }}
                        className="px-6 py-4 whitespace-nowrap text-slate-300 overflow-hidden text-ellipsis"
                      >
                        {col.render ? col.render(row) : row[col.key]}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      
      {/* Simple pagination footer placeholder */}
      <div className="p-3 border-t border-slate-700/50 bg-slate-800/30 text-xs text-slate-500 flex justify-between items-center">
        <span>Showing {processedData.length} records</span>
      </div>
    </div>
  );
}

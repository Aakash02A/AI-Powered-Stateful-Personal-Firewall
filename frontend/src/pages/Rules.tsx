import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Shield, Plus, Trash2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { fetchRules, deleteRule, createRule, FirewallRule } from '../api/rules';
import toast from 'react-hot-toast';
import { useForm } from 'react-hook-form';

export const Rules: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const { data: rules, isLoading, isError } = useQuery({
    queryKey: ['rules'],
    queryFn: fetchRules
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      toast.success('Rule deleted successfully');
    },
    onError: () => toast.error('Failed to delete rule')
  });

  const createMutation = useMutation({
    mutationFn: createRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      toast.success('Rule created successfully');
      setIsModalOpen(false);
      reset();
    },
    onError: () => toast.error('Failed to create rule')
  });

  const { register, handleSubmit, reset } = useForm<Omit<FirewallRule, 'rule_id'>>({
    defaultValues: {
      priority: 100,
      enabled: true,
      protocol: 'any',
      src_ip: 'any',
      src_port: 'any',
      dst_ip: 'any',
      dst_port: 'any',
      direction: 'both',
      action: 'allow',
      description: '',
      expires_at: null
    }
  });

  const onSubmit = (data: Omit<FirewallRule, 'rule_id'>) => {
    // Ensure priority is a number
    createMutation.mutate({
      ...data,
      priority: Number(data.priority)
    });
  };

  if (isLoading) {
    return <div className="p-6 text-slate-300">Loading rules...</div>;
  }

  if (isError) {
    return (
      <div className="p-6">
        <div className="bg-red-500/20 border border-red-500/50 p-4 rounded-lg flex items-center gap-3 text-red-200">
          <AlertCircle className="w-5 h-5" />
          <span>Failed to load firewall rules. Make sure the API is running.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/20 rounded-lg">
            <Shield className="w-6 h-6 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100">Rule Management</h1>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Rule
        </button>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800 border-b border-slate-700 text-slate-400 text-sm">
                <th className="p-4 font-medium">Priority</th>
                <th className="p-4 font-medium">Action</th>
                <th className="p-4 font-medium">Protocol</th>
                <th className="p-4 font-medium">Source</th>
                <th className="p-4 font-medium">Destination</th>
                <th className="p-4 font-medium">Direction</th>
                <th className="p-4 font-medium">Status</th>
                <th className="p-4 font-medium text-right">Manage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm">
              {rules?.map((rule) => (
                <tr key={rule.rule_id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="p-4 text-slate-300">{rule.priority}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                      rule.action === 'block' || rule.action === 'drop' 
                        ? 'bg-red-500/10 text-red-400 border-red-500/20' 
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    }`}>
                      {rule.action.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-slate-400">{rule.protocol.toUpperCase()}</td>
                  <td className="p-4 font-mono text-slate-400">
                    <div>{rule.src_ip}</div>
                    <div className="text-xs text-slate-500">Port: {rule.src_port}</div>
                  </td>
                  <td className="p-4 font-mono text-slate-400">
                    <div>{rule.dst_ip}</div>
                    <div className="text-xs text-slate-500">Port: {rule.dst_port}</div>
                  </td>
                  <td className="p-4 text-slate-300 capitalize">{rule.direction}</td>
                  <td className="p-4">
                    {rule.enabled ? (
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-1.5 text-emerald-400">
                          <CheckCircle className="w-4 h-4" /> <span className="text-xs">Enabled</span>
                        </div>
                        {rule.expires_at && (
                          <div className="text-[10px] text-slate-400 font-mono">
                            Expires: {new Date(rule.expires_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <XCircle className="w-4 h-4" /> <span className="text-xs">Disabled</span>
                      </div>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this rule?')) {
                          deleteMutation.mutate(rule.rule_id);
                        }
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-400/10 rounded transition-colors"
                      title="Delete Rule"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {rules?.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-500">
                    No firewall rules configured. All traffic is subject to default policies.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-700 flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-100">Create New Firewall Rule</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Action</label>
                  <select {...register('action')} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200">
                    <option value="allow">Allow</option>
                    <option value="block">Block</option>
                    <option value="drop">Drop</option>
                    <option value="log">Log Only</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Protocol</label>
                  <select {...register('protocol')} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200">
                    <option value="any">Any</option>
                    <option value="tcp">TCP</option>
                    <option value="udp">UDP</option>
                    <option value="icmp">ICMP</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Source IP / CIDR</label>
                  <input type="text" {...register('src_ip')} placeholder="any or 192.168.1.0/24" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Source Port</label>
                  <input type="text" {...register('src_port')} placeholder="any or 80" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Dest IP / CIDR</label>
                  <input type="text" {...register('dst_ip')} placeholder="any" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Dest Port</label>
                  <input type="text" {...register('dst_port')} placeholder="any" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Direction</label>
                  <select {...register('direction')} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200">
                    <option value="both">Both</option>
                    <option value="inbound">Inbound</option>
                    <option value="outbound">Outbound</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Priority (Lower is Higher)</label>
                  <input type="number" {...register('priority')} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                <input type="text" {...register('description')} placeholder="Why is this rule being added?" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200" />
              </div>

              <div className="flex items-center gap-2 mt-4">
                <input type="checkbox" id="enabled" {...register('enabled')} className="w-4 h-4 rounded border-slate-700 text-indigo-600 focus:ring-indigo-600 bg-slate-900" />
                <label htmlFor="enabled" className="text-sm font-medium text-slate-300">Rule Enabled</label>
              </div>

              <div className="flex justify-end gap-3 pt-6 border-t border-slate-700 mt-6">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-300 hover:text-white transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={createMutation.isPending} className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50">
                  {createMutation.isPending ? 'Saving...' : 'Save Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

import { apiClient } from './client';

export interface FirewallRule {
  rule_id: string;
  priority: number;
  enabled: boolean;
  protocol: string;
  src_ip: string;
  src_port: string;
  dst_ip: string;
  dst_port: string;
  direction: string;
  action: string;
  description: string;
  expires_at?: string;
}

export const fetchRules = async (): Promise<FirewallRule[]> => {
  const { data } = await apiClient.get<{ rules: FirewallRule[] }>('/rules/');
  return data.rules;
};

export const createRule = async (rule: Omit<FirewallRule, 'rule_id'>): Promise<FirewallRule> => {
  const { data } = await apiClient.post<{ status: string; rule: FirewallRule }>('/rules/', rule);
  return data.rule;
};

export const deleteRule = async (ruleId: string): Promise<void> => {
  await apiClient.delete(`/rules/${ruleId}`);
};

export const updateRule = async (ruleId: string, rule: Omit<FirewallRule, 'rule_id'>): Promise<FirewallRule> => {
  const { data } = await apiClient.put<{ status: string; rule: FirewallRule }>(`/rules/${ruleId}`, rule);
  return data.rule;
};

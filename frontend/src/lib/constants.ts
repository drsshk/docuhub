export const STATUS_COLORS = {
  pending: { label: "Pending", variant: "warning" },
  approved: { label: "Approved", variant: "success" },
  rejected: { label: "Rejected", variant: "destructive" },
  submitted: { label: "Submitted", variant: "info" },
  draft: { label: "Draft", variant: "secondary" },
};

export type StatusType = keyof typeof STATUS_COLORS;

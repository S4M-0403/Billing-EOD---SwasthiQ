export interface PaymentModeReport {
  billed_paise: number;
  collected_paise: number;
  outstanding_paise: number;
  refunds_paise: number;
}

export interface ReconciliationReport {
  total_billed_paise: number;
  total_collected_paise: number;
  total_outstanding_paise: number;
  total_refunds_paise: number;
  by_payment_mode: Record<
    string,
    PaymentModeReport
  >;
}

export interface AnalyticsReport {
  revenue_by_hour: {
    hour: number;
    revenue_paise: number;
  }[];

  peak_hour: number | null;

  top_medicines_by_quantity: {
    drug_name: string;
    quantity: number;
  }[];

  top_medicines_by_revenue: {
    drug_name: string;
    revenue_paise: number;
  }[];
}

export interface EODReport {
  clinic_id: string;
  report_date: string;
  reconciliation: ReconciliationReport;
  analytics: AnalyticsReport;
}

export interface Narrative {
  narrative: string;
  traced_figures: {
    token: string;
    display_value: string;
    source: string;
  }[];
}
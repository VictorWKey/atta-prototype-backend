# ATTA MONTACARGAS API - TypeScript Types & Examples

## TypeScript Interfaces

```typescript
// Base interfaces
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'jefe' | 'operador';
  position: string | null;
  avatar: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

interface Client {
  id: number;
  name: string;
  address: string;
  created_at: string;
  updated_at: string | null;
  contacts: Contact[];
}

interface Contact {
  id: number;
  client_id: number;
  name: string;
  position: string | null;
  phone: string | null;
  email: string | null;
  created_at: string;
}

interface Equipment {
  id: number;
  type: 'Combustión' | 'Eléctrico' | 'Manual' | 'Otro';
  brand: string;
  model: string;
  serial_number: string;
  created_at: string;
  updated_at: string | null;
}

interface OperationPoints {
  velocidad_avance: number | null;
  funciones_auxiliares_operando: 'SÍ' | 'NO' | 'N/A' | null;
  paro_emergencia_especificaciones: 'SÍ' | 'NO' | 'N/A' | null;
}

interface InspectionItem {
  id: string;
  name: string;
  category: string;
  status: 'OK' | 'N/A' | 'R';
  notes: string | null;
}

interface AppliedPart {
  description: string;
  quantity: number;
}

interface WorkTime {
  date: string;
  entryTime: string;
  exitTime: string;
  totalHours: number;
}

interface PossibleCause {
  id: string;
  name: string;
  selected: boolean;
}

interface ServiceReport {
  id: number;
  report_number: number;
  date: string;
  created_by: number;
  client_id: number;
  requested_by_id: number;
  equipment_id: number;
  technician_id: number;
  service_type: 'Preventivo' | 'Correctivo' | 'Instalación' | 'Reparación' | 'Otro';
  billing_type: 'Facturación' | 'Renta' | 'Garantía' | 'Sin costo';
  battery_percentage: number | null;
  horometer_readings: Record<string, number>;
  work_performed: string | null;
  detected_damages: string | null;
  possible_causes: PossibleCause[] | null;
  activities_performed: string | null;
  operation_points: OperationPoints | null;
  inspection_items: InspectionItem[] | null;
  technician_comments: string | null;
  applied_parts: AppliedPart[] | null;
  work_time: WorkTime | null;
  status: 'pending' | 'completed';
  client_signature: string | null;
  technician_signature: string | null;
  created_at: string;
  updated_at: string | null;
  technician: User;
  client: Client;
  requested_by: Contact;
  equipment: Equipment;
}

// Request interfaces
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
  role: 'admin' | 'jefe' | 'operador';
  position?: string;
  avatar?: string;
}

interface CreateClientRequest {
  name: string;
  address: string;
}

interface CreateContactRequest {
  name: string;
  position?: string;
  phone?: string;
  email?: string;
}

interface CreateEquipmentRequest {
  type: 'Combustión' | 'Eléctrico' | 'Manual' | 'Otro';
  brand: string;
  model: string;
  serial_number: string;
}

interface CreateServiceReportRequest {
  date: string;
  client_id: number;
  requested_by_id: number;
  equipment_id: number;
  service_type: 'Preventivo' | 'Correctivo' | 'Instalación' | 'Reparación' | 'Otro';
  billing_type: 'Facturación' | 'Renta' | 'Garantía' | 'Sin costo';
  battery_percentage?: number;
  horometer_readings?: Record<string, number>;
  work_performed?: string;
  detected_damages?: string;
  possible_causes?: PossibleCause[];
  activities_performed?: string;
  operation_points?: OperationPoints;
  inspection_items?: InspectionItem[];
  technician_comments?: string;
  applied_parts?: AppliedPart[];
  work_time?: WorkTime;
}

interface DashboardStats {
  total_reports: number;
  pending_reports: number;
  completed_reports: number;
  client_count?: number;
  technician_count?: number;
  equipment_count?: number;
}

interface InspectionCategory {
  id: number;
  name: string;
  description: string | null;
  order_index: number;
  is_active: boolean;
  created_at: string;
}

interface InspectionItemTemplate {
  id: number;
  category_id: number;
  name: string;
  description: string | null;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

interface ServiceReportTemplates {
  inspection_categories: Record<string, Array<{
    id: string;
    name: string;
    category: string;
    description: string | null;
  }>>;
  operation_points: Record<string, {
    display_name: string;
    field_type: string;
    options: string[] | null;
    validation_rules: Record<string, any> | null;
  }>;
  status_options: Record<string, string>;
}
```

## API Service Class Example

```typescript
class AttaApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  }

  // Authentication
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    const result = await this.handleResponse<LoginResponse>(response);
    this.token = result.access_token;
    return result;
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/auth/me`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<User>(response);
  }

  logout(): void {
    this.token = null;
  }

  // Users
  async getUsers(): Promise<User[]> {
    const response = await fetch(`${this.baseUrl}/api/users/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<User[]>(response);
  }

  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/users/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });
    return this.handleResponse<User>(response);
  }

  // Clients
  async getClients(): Promise<Client[]> {
    const response = await fetch(`${this.baseUrl}/api/clients/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Client[]>(response);
  }

  async createClient(clientData: CreateClientRequest): Promise<Client> {
    const response = await fetch(`${this.baseUrl}/api/clients/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(clientData),
    });
    return this.handleResponse<Client>(response);
  }

  async getClientContacts(clientId: number): Promise<Contact[]> {
    const response = await fetch(`${this.baseUrl}/api/clients/${clientId}/contacts`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Contact[]>(response);
  }

  async createContact(clientId: number, contactData: CreateContactRequest): Promise<Contact> {
    const response = await fetch(`${this.baseUrl}/api/clients/${clientId}/contacts`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(contactData),
    });
    return this.handleResponse<Contact>(response);
  }

  // Equipment
  async getEquipment(type?: string): Promise<Equipment[]> {
    const url = new URL(`${this.baseUrl}/api/equipment/`);
    if (type) {
      url.searchParams.set('equipment_type', type);
    }
    
    const response = await fetch(url.toString(), {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Equipment[]>(response);
  }

  async createEquipment(equipmentData: CreateEquipmentRequest): Promise<Equipment> {
    const response = await fetch(`${this.baseUrl}/api/equipment/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(equipmentData),
    });
    return this.handleResponse<Equipment>(response);
  }

  async getEquipmentTypes(): Promise<{ types: string[] }> {
    const response = await fetch(`${this.baseUrl}/api/equipment/types/list`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<{ types: string[] }>(response);
  }

  // Service Reports
  async getServiceReports(filters?: {
    status_filter?: string;
    client_id?: number;
    technician_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<ServiceReport[]> {
    const url = new URL(`${this.baseUrl}/api/service-reports/`);
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.set(key, value.toString());
        }
      });
    }
    
    const response = await fetch(url.toString(), {
      headers: this.getHeaders(),
    });
    return this.handleResponse<ServiceReport[]>(response);
  }

  async getServiceReport(id: number): Promise<ServiceReport> {
    const response = await fetch(`${this.baseUrl}/api/service-reports/${id}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<ServiceReport>(response);
  }

  async createServiceReport(reportData: CreateServiceReportRequest): Promise<ServiceReport> {
    const response = await fetch(`${this.baseUrl}/api/service-reports/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(reportData),
    });
    return this.handleResponse<ServiceReport>(response);
  }

  async updateServiceReport(id: number, reportData: Partial<CreateServiceReportRequest>): Promise<ServiceReport> {
    const response = await fetch(`${this.baseUrl}/api/service-reports/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(reportData),
    });
    return this.handleResponse<ServiceReport>(response);
  }

  async uploadSignature(reportId: number, signatureType: 'client' | 'technician', file: File): Promise<{ message: string; file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${this.baseUrl}/api/service-reports/${reportId}/upload-signature?signature_type=${signatureType}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
        body: formData,
      }
    );
    return this.handleResponse<{ message: string; file_path: string }>(response);
  }

  async downloadReportPDF(reportId: number): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/service-reports/${reportId}/pdf`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to download PDF: ${response.status}`);
    }
    
    return response.blob();
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await fetch(`${this.baseUrl}/api/service-reports/statistics/dashboard`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<DashboardStats>(response);
  }

  // Inspection
  async getInspectionCategories(): Promise<InspectionCategory[]> {
    const response = await fetch(`${this.baseUrl}/api/inspection/categories`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<InspectionCategory[]>(response);
  }

  async getInspectionItems(categoryId: number): Promise<InspectionItemTemplate[]> {
    const response = await fetch(`${this.baseUrl}/api/inspection/categories/${categoryId}/items`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<InspectionItemTemplate[]>(response);
  }

  async getServiceReportTemplates(): Promise<ServiceReportTemplates> {
    const response = await fetch(`${this.baseUrl}/api/inspection/templates/service-report`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<ServiceReportTemplates>(response);
  }
}

// Usage example
const api = new AttaApiService();

// In your app
async function initializeApp() {
  try {
    // Login
    await api.login('admin@attamontacargas.com', 'password123');
    
    // Get current user
    const user = await api.getCurrentUser();
    console.log('Current user:', user);
    
    // Get dashboard stats
    const stats = await api.getDashboardStats();
    console.log('Dashboard stats:', stats);
    
    // Get service reports
    const reports = await api.getServiceReports({ status_filter: 'pending' });
    console.log('Pending reports:', reports);
    
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

## React Hooks Examples

```typescript
// useAuth hook
import { useState, useEffect, createContext, useContext } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const api = new AttaApiService();

  useEffect(() => {
    // Check for existing token in localStorage
    const token = localStorage.getItem('atta_token');
    if (token) {
      api.token = token;
      api.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('atta_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    localStorage.setItem('atta_token', response.access_token);
    const userData = await api.getCurrentUser();
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('atta_token');
    api.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// useServiceReports hook
import { useState, useEffect } from 'react';

export function useServiceReports(filters?: {
  status_filter?: string;
  client_id?: number;
}) {
  const [reports, setReports] = useState<ServiceReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const api = new AttaApiService();

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const data = await api.getServiceReports(filters);
        setReports(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [JSON.stringify(filters)]);

  const createReport = async (reportData: CreateServiceReportRequest) => {
    const newReport = await api.createServiceReport(reportData);
    setReports(prev => [newReport, ...prev]);
    return newReport;
  };

  const updateReport = async (id: number, reportData: Partial<CreateServiceReportRequest>) => {
    const updatedReport = await api.updateServiceReport(id, reportData);
    setReports(prev => prev.map(r => r.id === id ? updatedReport : r));
    return updatedReport;
  };

  return {
    reports,
    loading,
    error,
    createReport,
    updateReport,
    refresh: () => {
      const fetchReports = async () => {
        const data = await api.getServiceReports(filters);
        setReports(data);
      };
      fetchReports();
    }
  };
}
```

## Error Handling

```typescript
// Error types
interface ApiError {
  detail: string;
}

interface ValidationError {
  detail: Array<{
    type: string;
    loc: string[];
    msg: string;
    input: any;
  }>;
}

// Error handler utility
export function handleApiError(error: any): string {
  if (error.response) {
    const data = error.response.data;
    if (Array.isArray(data.detail)) {
      // Validation errors
      return data.detail.map((err: any) => err.msg).join(', ');
    }
    return data.detail || 'Unknown server error';
  }
  return error.message || 'Network error';
}

// Use in components
try {
  await api.createServiceReport(reportData);
} catch (error) {
  const errorMessage = handleApiError(error);
  // Show error to user
  console.error(errorMessage);
}
```

## Local Storage Utilities

```typescript
// Token management
export const tokenManager = {
  getToken: (): string | null => {
    return localStorage.getItem('atta_token');
  },
  
  setToken: (token: string): void => {
    localStorage.setItem('atta_token', token);
  },
  
  removeToken: (): void => {
    localStorage.removeItem('atta_token');
  },
  
  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp < Date.now() / 1000;
    } catch {
      return true;
    }
  }
};

// Form data persistence
export const formStorage = {
  saveReport: (reportId: string, data: Partial<CreateServiceReportRequest>): void => {
    localStorage.setItem(`report_draft_${reportId}`, JSON.stringify(data));
  },
  
  getReport: (reportId: string): Partial<CreateServiceReportRequest> | null => {
    const data = localStorage.getItem(`report_draft_${reportId}`);
    return data ? JSON.parse(data) : null;
  },
  
  clearReport: (reportId: string): void => {
    localStorage.removeItem(`report_draft_${reportId}`);
  }
};
```

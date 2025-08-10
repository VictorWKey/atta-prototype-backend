# ATTA MONTACARGAS API - Environment Configuration

## Environment Variables for Frontend

Create a `.env` file in your frontend project with these variables:

### Development
```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_VERSION=v1

# JWT Configuration
REACT_APP_JWT_STORAGE_KEY=atta_token
REACT_APP_JWT_REFRESH_THRESHOLD=3600 # 1 hour before expiry

# File Upload Configuration
REACT_APP_MAX_FILE_SIZE=10485760 # 10MB in bytes
REACT_APP_ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg

# Pagination Defaults
REACT_APP_DEFAULT_PAGE_SIZE=20
REACT_APP_MAX_PAGE_SIZE=100

# Feature Flags
REACT_APP_ENABLE_SIGNATURE_UPLOAD=true
REACT_APP_ENABLE_PDF_DOWNLOAD=true
REACT_APP_ENABLE_OFFLINE_MODE=false

# Error Tracking (optional)
REACT_APP_SENTRY_DSN=your_sentry_dsn_here
```

### Production
```bash
# API Configuration
REACT_APP_API_BASE_URL=https://api.attamontacargas.com
REACT_APP_API_VERSION=v1

# JWT Configuration
REACT_APP_JWT_STORAGE_KEY=atta_token
REACT_APP_JWT_REFRESH_THRESHOLD=3600

# File Upload Configuration
REACT_APP_MAX_FILE_SIZE=10485760
REACT_APP_ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg

# Pagination Defaults
REACT_APP_DEFAULT_PAGE_SIZE=20
REACT_APP_MAX_PAGE_SIZE=100

# Feature Flags
REACT_APP_ENABLE_SIGNATURE_UPLOAD=true
REACT_APP_ENABLE_PDF_DOWNLOAD=true
REACT_APP_ENABLE_OFFLINE_MODE=true

# Error Tracking
REACT_APP_SENTRY_DSN=your_production_sentry_dsn
```

## TypeScript Configuration for API

Add this to your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src",
    "src/types/api.ts" // Your API types file
  ]
}
```

## Package Dependencies

Essential packages for frontend integration:

```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "react-hook-form": "^7.43.0",
    "react-query": "^3.39.0", // or @tanstack/react-query for v4+
    "date-fns": "^2.29.0",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@types/uuid": "^9.0.0",
    "typescript": "^4.9.0"
  }
}
```

## API Client Configuration

Create `src/config/api.ts`:

```typescript
interface ApiConfig {
  baseURL: string;
  timeout: number;
  maxFileSize: number;
  allowedImageTypes: string[];
  jwtStorageKey: string;
  jwtRefreshThreshold: number;
}

export const apiConfig: ApiConfig = {
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  maxFileSize: parseInt(process.env.REACT_APP_MAX_FILE_SIZE || '10485760'),
  allowedImageTypes: (process.env.REACT_APP_ALLOWED_IMAGE_TYPES || 'image/jpeg,image/png').split(','),
  jwtStorageKey: process.env.REACT_APP_JWT_STORAGE_KEY || 'atta_token',
  jwtRefreshThreshold: parseInt(process.env.REACT_APP_JWT_REFRESH_THRESHOLD || '3600'),
};

// Validate required environment variables
const requiredEnvVars = ['REACT_APP_API_BASE_URL'];

requiredEnvVars.forEach(varName => {
  if (!process.env[varName]) {
    console.warn(`Warning: Required environment variable ${varName} is not set`);
  }
});
```

## Axios Configuration

Create `src/services/httpClient.ts`:

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiConfig } from '../config/api';
import { tokenManager } from '../utils/tokenManager';

// Create axios instance
const httpClient: AxiosInstance = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
httpClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = tokenManager.getToken();
    if (token && !tokenManager.isTokenExpired(token)) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
httpClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      tokenManager.removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default httpClient;
```

## Form Validation Schemas

Using Yup for form validation:

```bash
npm install yup @types/yup
```

Create `src/schemas/validation.ts`:

```typescript
import * as yup from 'yup';

export const loginSchema = yup.object({
  email: yup.string().email('Email inválido').required('Email es requerido'),
  password: yup.string().min(6, 'Mínimo 6 caracteres').required('Contraseña es requerida'),
});

export const serviceReportSchema = yup.object({
  date: yup.string().required('Fecha es requerida'),
  client_id: yup.number().required('Cliente es requerido'),
  requested_by_id: yup.number().required('Contacto es requerido'),
  equipment_id: yup.number().required('Equipo es requerido'),
  service_type: yup.string().oneOf(['Preventivo', 'Correctivo', 'Instalación', 'Reparación', 'Otro']).required(),
  billing_type: yup.string().oneOf(['Facturación', 'Renta', 'Garantía', 'Sin costo']).required(),
  battery_percentage: yup.number().min(0).max(100).nullable(),
  horometer_readings: yup.object().default({}),
  work_performed: yup.string().nullable(),
  detected_damages: yup.string().nullable(),
  activities_performed: yup.string().nullable(),
  technician_comments: yup.string().nullable(),
});

export const userSchema = yup.object({
  name: yup.string().required('Nombre es requerido'),
  email: yup.string().email('Email inválido').required('Email es requerido'),
  password: yup.string().min(6, 'Mínimo 6 caracteres').required('Contraseña es requerida'),
  role: yup.string().oneOf(['admin', 'jefe', 'operador']).required(),
  position: yup.string().nullable(),
});

export const clientSchema = yup.object({
  name: yup.string().required('Nombre es requerido'),
  address: yup.string().required('Dirección es requerida'),
});

export const equipmentSchema = yup.object({
  type: yup.string().oneOf(['Combustión', 'Eléctrico', 'Manual', 'Otro']).required(),
  brand: yup.string().required('Marca es requerida'),
  model: yup.string().required('Modelo es requerido'),
  serial_number: yup.string().required('Número de serie es requerido'),
});
```

## Constants

Create `src/constants/api.ts`:

```typescript
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/auth/login',
  CURRENT_USER: '/api/auth/me',
  
  // Users
  USERS: '/api/users',
  USER_BY_ID: (id: number) => `/api/users/${id}`,
  
  // Clients
  CLIENTS: '/api/clients',
  CLIENT_BY_ID: (id: number) => `/api/clients/${id}`,
  CLIENT_CONTACTS: (clientId: number) => `/api/clients/${clientId}/contacts`,
  
  // Equipment
  EQUIPMENT: '/api/equipment',
  EQUIPMENT_BY_ID: (id: number) => `/api/equipment/${id}`,
  EQUIPMENT_TYPES: '/api/equipment/types/list',
  
  // Service Reports
  SERVICE_REPORTS: '/api/service-reports',
  SERVICE_REPORT_BY_ID: (id: number) => `/api/service-reports/${id}`,
  SERVICE_REPORT_PDF: (id: number) => `/api/service-reports/${id}/pdf`,
  UPLOAD_SIGNATURE: (id: number, type: string) => `/api/service-reports/${id}/upload-signature?signature_type=${type}`,
  DASHBOARD_STATS: '/api/service-reports/statistics/dashboard',
  
  // Inspection
  INSPECTION_CATEGORIES: '/api/inspection/categories',
  INSPECTION_ITEMS: (categoryId: number) => `/api/inspection/categories/${categoryId}/items`,
  SERVICE_REPORT_TEMPLATES: '/api/inspection/templates/service-report',
} as const;

export const ROLES = {
  ADMIN: 'admin',
  JEFE: 'jefe', 
  OPERADOR: 'operador',
} as const;

export const SERVICE_TYPES = [
  'Preventivo',
  'Correctivo', 
  'Instalación',
  'Reparación',
  'Otro'
] as const;

export const BILLING_TYPES = [
  'Facturación',
  'Renta',
  'Garantía',
  'Sin costo'
] as const;

export const EQUIPMENT_TYPES = [
  'Combustión',
  'Eléctrico',
  'Manual',
  'Otro'
] as const;

export const INSPECTION_STATUS = {
  OK: 'OK',
  NA: 'N/A',
  R: 'R',
} as const;

export const REPORT_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
} as const;
```

## Error Messages

Create `src/constants/messages.ts`:

```typescript
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifica tu conexión a internet.',
  UNAUTHORIZED: 'Sesión expirada. Por favor inicia sesión nuevamente.',
  FORBIDDEN: 'No tienes permisos para realizar esta acción.',
  NOT_FOUND: 'El recurso solicitado no fue encontrado.',
  VALIDATION_ERROR: 'Por favor verifica los datos ingresados.',
  SERVER_ERROR: 'Error interno del servidor. Intenta nuevamente.',
  FILE_TOO_LARGE: 'El archivo es demasiado grande. Máximo 10MB.',
  INVALID_FILE_TYPE: 'Tipo de archivo no válido. Solo se permiten imágenes JPEG y PNG.',
} as const;

export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Inicio de sesión exitoso',
  REPORT_CREATED: 'Reporte creado exitosamente',
  REPORT_UPDATED: 'Reporte actualizado exitosamente',
  USER_CREATED: 'Usuario creado exitosamente',
  CLIENT_CREATED: 'Cliente creado exitosamente',
  EQUIPMENT_CREATED: 'Equipo creado exitosamente',
  SIGNATURE_UPLOADED: 'Firma subida exitosamente',
  PDF_GENERATED: 'PDF generado exitosamente',
} as const;
```

## Testing Configuration

Create `src/test-utils/api-mocks.ts`:

```typescript
// Mock data for testing
export const mockUser = {
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  role: 'admin' as const,
  position: 'Test Position',
  avatar: null,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: null,
};

export const mockClient = {
  id: 1,
  name: 'Test Client',
  address: 'Test Address',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: null,
  contacts: [],
};

// API Mock responses
export const mockApiResponses = {
  login: {
    access_token: 'mock-jwt-token',
    token_type: 'bearer',
  },
  currentUser: mockUser,
  clients: [mockClient],
  serviceReports: [],
  dashboardStats: {
    total_reports: 0,
    pending_reports: 0,
    completed_reports: 0,
    client_count: 1,
    technician_count: 1,
    equipment_count: 0,
  },
};
```

This documentation provides everything the frontend team needs to successfully integrate with the ATTA MONTACARGAS backend API!

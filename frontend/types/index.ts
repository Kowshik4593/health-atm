// frontend/types/index.ts

// --- ML & Findings Types ---

export interface User {
    id: string;
    email: string;
    role: 'doctor' | 'operator' | 'patient';
    full_name?: string;
}

export interface Uncertainty {
    confidence: number;
    entropy: number;
    needs_review: boolean;
}

export interface BoundingBox {
    z: [number, number];
    y: [number, number];
    x: [number, number];
}

export interface Nodule {
    id: number;
    centroid: [number, number, number];
    bbox: BoundingBox;
    long_axis_mm: number;
    volume_mm3: number;
    type: 'solid' | 'subsolid' | 'ground-glass' | 'suspicious' | 'indeterminate' | 'benign';
    location: string;
    prob_malignant: number;
    uncertainty: Uncertainty;
    mask_path: string;
}

export interface Findings {
    study_id: string; // This maps to the Case ID (UUID)
    patient_name?: string;
    patient_age?: number;
    patient_gender?: string;
    scan_date?: string;
    lung_health: string;
    airway_wall_thickness: string;
    emphysema_score: number;
    fibrosis_score: number;
    consolidation_score: number;
    impression: string;
    summary_text: string;
    num_nodules: number;
    nodules: Nodule[];
    processing_time_seconds?: number;
}

export type RiskLevel = 'high' | 'medium' | 'low';

export interface UploadResponse {
    scan_id: string;
    filename: string;
    size_bytes: number;
    status: 'uploaded' | 'processing' | 'completed' | 'failed';
}

// --- Database Entities (Supabase) ---

export interface Profile {
    id: string; // UUID
    full_name: string;
    email?: string; // Optional (joined from auth)
    dob: string;
    gender: 'male' | 'female' | 'other';
    phone: string;
    role: 'doctor' | 'operator' | 'patient';
    role_locked?: boolean;
    masked_aadhar?: string;
    country?: string;
    state?: string;
    city?: string;
    postal_code?: string;
    primary_language?: string;

    // Doctor specific
    license_number?: string;
    hospital?: string;
    specialization?: string;
    qualifications?: string;
    availability?: string;

    // Operator specific
    organization?: string;
    center_location?: string;
    operator_contact?: string;

    // Patient specific
    medical_history?: string;
    emergency_contact?: string;

    created_at?: string;
    updated_at?: string;
}

// Matches 'patient_ct_scans' table
export interface Case {
    id: string; // UUID
    patient_id: string;
    uploaded_at: string;
    storage_path: string;
    status: 'uploaded' | 'processing' | 'completed' | 'failed';
    updated_at: string;

    // Joined Data (Optional)
    patient?: Profile;
    results?: ScanResult;
    assignment?: DoctorAssignment;
}

// Matches 'scan_results' table
export interface ScanResult {
    id: string; // UUID
    scan_id: string;
    findings_json: Findings;
    clinician_pdf: string | null; // Path in 'reports' bucket
    patient_pdf: string | null;   // Path in 'reports' bucket
    generated_at: string;
}

// Matches 'doctor_assignments' table
export interface DoctorAssignment {
    id: string; // UUID
    scan_id: string;
    doctor_id: string;
    accepted_at: string;
    status: 'assigned' | 'completed';

    // Joined Data
    doctor?: Profile;
    scan?: Case;
}

// Matches 'chat_messages' table
export interface Message {
    id: string; // UUID
    assignment_id: string; // Links to the doctor assignment
    sender_id: string;
    message: string;
    attachment_url?: string;
    sent_at: string;

    // UI Helpers
    is_me?: boolean; // Calculated on frontend
}

// Represents a Chat Room (Derived from Assignment)
export interface Chat {
    assignment_id: string;
    case_id: string;
    doctor: Profile;
    patient: Profile;
    last_message?: Message;
}

// Matches 'notifications' table
export interface Notification {
    id: string; // UUID
    user_id: string;
    message: string;
    is_read: boolean;
    created_at: string;

    // Optional: Action link type
    type?: 'report_ready' | 'case_assigned' | 'new_message';
    reference_id?: string; // scan_id or assignment_id
}
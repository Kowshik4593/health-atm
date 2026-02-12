// frontend/components/PatientForm.tsx

'use client';

import { useState } from 'react';

interface PatientFormData {
    full_name: string;
    phone: string;
    dob: string;
    gender: 'male' | 'female' | 'other';
    email?: string;
}

interface PatientFormProps {
    onSubmit: (data: PatientFormData) => Promise<void>;
    onCancel: () => void;
    loading?: boolean;
    isDark?: boolean;
}

export default function PatientForm({
    onSubmit,
    onCancel,
    loading = false,
    isDark = false,
}: PatientFormProps) {
    const [formData, setFormData] = useState<PatientFormData>({
        full_name: '',
        phone: '',
        dob: '',
        gender: 'male',
        email: '',
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    const validate = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.full_name.trim()) {
            newErrors.full_name = 'Full name is required';
        }

        if (!formData.phone.trim()) {
            newErrors.phone = 'Phone number is required';
        } else if (!/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
            newErrors.phone = 'Enter a valid 10-digit phone number';
        }

        if (!formData.dob) {
            newErrors.dob = 'Date of birth is required';
        }

        if (!formData.gender) {
            newErrors.gender = 'Gender is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (validate()) {
            await onSubmit(formData);
        }
    };

    const handleChange = (field: keyof PatientFormData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: '' }));
        }
    };

    const styles = {
        form: {
            display: 'flex',
            flexDirection: 'column' as const,
            gap: '20px',
        },
        field: {
            display: 'flex',
            flexDirection: 'column' as const,
            gap: '6px',
        },
        label: {
            fontSize: '14px',
            fontWeight: 500,
            color: isDark ? '#e5e5e5' : '#171717',
        },
        required: {
            color: '#ef4444',
            marginLeft: '2px',
        },
        input: {
            padding: '12px 14px',
            borderRadius: '8px',
            border: `1px solid ${isDark ? '#404040' : '#d4d4d4'}`,
            backgroundColor: isDark ? '#0a0a0a' : '#ffffff',
            color: isDark ? '#ffffff' : '#171717',
            fontSize: '14px',
            outline: 'none',
            transition: 'border-color 0.15s',
        },
        inputError: {
            borderColor: '#ef4444',
        },
        select: {
            padding: '12px 14px',
            borderRadius: '8px',
            border: `1px solid ${isDark ? '#404040' : '#d4d4d4'}`,
            backgroundColor: isDark ? '#0a0a0a' : '#ffffff',
            color: isDark ? '#ffffff' : '#171717',
            fontSize: '14px',
            outline: 'none',
            cursor: 'pointer',
        },
        error: {
            fontSize: '12px',
            color: '#ef4444',
        },
        actions: {
            display: 'flex',
            gap: '12px',
            marginTop: '12px',
        },
        btn: {
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            border: 'none',
            transition: 'all 0.15s',
            flex: 1,
        },
        btnPrimary: {
            backgroundColor: isDark ? '#ffffff' : '#171717',
            color: isDark ? '#000000' : '#ffffff',
        },
        btnSecondary: {
            backgroundColor: isDark ? '#262626' : '#f5f5f5',
            color: isDark ? '#ffffff' : '#171717',
        },
        btnDisabled: {
            opacity: 0.5,
            cursor: 'not-allowed',
        },
        genderGroup: {
            display: 'flex',
            gap: '12px',
        },
        genderOption: {
            flex: 1,
            padding: '12px',
            borderRadius: '8px',
            border: `1px solid ${isDark ? '#404040' : '#d4d4d4'}`,
            backgroundColor: isDark ? '#0a0a0a' : '#ffffff',
            color: isDark ? '#a3a3a3' : '#525252',
            fontSize: '14px',
            cursor: 'pointer',
            textAlign: 'center' as const,
            transition: 'all 0.15s',
        },
        genderOptionSelected: {
            backgroundColor: isDark ? '#ffffff' : '#171717',
            color: isDark ? '#000000' : '#ffffff',
            borderColor: isDark ? '#ffffff' : '#171717',
        },
    };

    return (
        <form style={styles.form} onSubmit={handleSubmit}>
            {/* Full Name */}
            <div style={styles.field}>
                <label style={styles.label}>
                    Full Name<span style={styles.required}>*</span>
                </label>
                <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => handleChange('full_name', e.target.value)}
                    placeholder="Enter patient's full name"
                    style={{
                        ...styles.input,
                        ...(errors.full_name ? styles.inputError : {}),
                    }}
                />
                {errors.full_name && <span style={styles.error}>{errors.full_name}</span>}
            </div>

            {/* Phone */}
            <div style={styles.field}>
                <label style={styles.label}>
                    Phone Number<span style={styles.required}>*</span>
                </label>
                <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    placeholder="10-digit phone number"
                    style={{
                        ...styles.input,
                        ...(errors.phone ? styles.inputError : {}),
                    }}
                />
                {errors.phone && <span style={styles.error}>{errors.phone}</span>}
            </div>

            {/* Date of Birth */}
            <div style={styles.field}>
                <label style={styles.label}>
                    Date of Birth<span style={styles.required}>*</span>
                </label>
                <input
                    type="date"
                    value={formData.dob}
                    onChange={(e) => handleChange('dob', e.target.value)}
                    style={{
                        ...styles.input,
                        ...(errors.dob ? styles.inputError : {}),
                    }}
                />
                {errors.dob && <span style={styles.error}>{errors.dob}</span>}
            </div>

            {/* Gender */}
            <div style={styles.field}>
                <label style={styles.label}>
                    Gender<span style={styles.required}>*</span>
                </label>
                <div style={styles.genderGroup}>
                    {(['male', 'female', 'other'] as const).map((gender) => (
                        <div
                            key={gender}
                            style={{
                                ...styles.genderOption,
                                ...(formData.gender === gender ? styles.genderOptionSelected : {}),
                            }}
                            onClick={() => handleChange('gender', gender)}
                        >
                            {gender.charAt(0).toUpperCase() + gender.slice(1)}
                        </div>
                    ))}
                </div>
                {errors.gender && <span style={styles.error}>{errors.gender}</span>}
            </div>

            {/* Email (Optional) */}
            <div style={styles.field}>
                <label style={styles.label}>Email (Optional)</label>
                <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    placeholder="patient@email.com"
                    style={styles.input}
                />
            </div>

            {/* Actions */}
            <div style={styles.actions}>
                <button
                    type="button"
                    style={{ ...styles.btn, ...styles.btnSecondary }}
                    onClick={onCancel}
                    disabled={loading}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    style={{
                        ...styles.btn,
                        ...styles.btnPrimary,
                        ...(loading ? styles.btnDisabled : {}),
                    }}
                    disabled={loading}
                >
                    {loading ? 'Creating...' : 'Create Patient'}
                </button>
            </div>
        </form>
    );
}
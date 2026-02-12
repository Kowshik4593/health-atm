// frontend/app/complete-profile/page.tsx

'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import supabase from '../../lib/supabaseClient';

type Role = 'doctor' | 'operator' | 'patient';

// Type definition for Profile Insert to replace 'any'
interface ProfileInsert {
  id: string;
  full_name: string;
  dob: string;
  gender: string;
  primary_language: string;
  masked_aadhar: string | null;
  phone: string;
  country: string;
  state: string;
  city: string;
  postal_code: string;
  role: Role;
  role_locked: boolean;
  updated_at: string;

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
}

// India location data (complete dataset)
const INDIA_STATES: Record<string, { cities: string[], pincodes: Record<string, string> }> = {
  'Andhra Pradesh': {
    cities: ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Tirupati'],
    pincodes: { 'Visakhapatnam': '530001', 'Vijayawada': '520001', 'Guntur': '522001', 'Nellore': '524001', 'Kurnool': '518001', 'Tirupati': '517501' }
  },
  'Arunachal Pradesh': {
    cities: ['Itanagar', 'Naharlagun', 'Pasighat', 'Tawang'],
    pincodes: { 'Itanagar': '791111', 'Naharlagun': '791110', 'Pasighat': '791102', 'Tawang': '790104' }
  },
  'Assam': {
    cities: ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia'],
    pincodes: { 'Guwahati': '781001', 'Silchar': '788001', 'Dibrugarh': '786001', 'Jorhat': '785001', 'Nagaon': '782001', 'Tinsukia': '786125' }
  },
  'Bihar': {
    cities: ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga'],
    pincodes: { 'Patna': '800001', 'Gaya': '823001', 'Bhagalpur': '812001', 'Muzaffarpur': '842001', 'Purnia': '854301', 'Darbhanga': '846001' }
  },
  'Chhattisgarh': {
    cities: ['Raipur', 'Bhilai', 'Bilaspur', 'Korba', 'Durg', 'Rajnandgaon'],
    pincodes: { 'Raipur': '492001', 'Bhilai': '490001', 'Bilaspur': '495001', 'Korba': '495677', 'Durg': '491001', 'Rajnandgaon': '491441' }
  },
  'Goa': {
    cities: ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda'],
    pincodes: { 'Panaji': '403001', 'Margao': '403601', 'Vasco da Gama': '403802', 'Mapusa': '403507', 'Ponda': '403401' }
  },
  'Gujarat': {
    cities: ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Gandhinagar'],
    pincodes: { 'Ahmedabad': '380001', 'Surat': '395001', 'Vadodara': '390001', 'Rajkot': '360001', 'Bhavnagar': '364001', 'Jamnagar': '361001', 'Gandhinagar': '382010' }
  },
  'Haryana': {
    cities: ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar'],
    pincodes: { 'Faridabad': '121001', 'Gurgaon': '122001', 'Panipat': '132103', 'Ambala': '134001', 'Yamunanagar': '135001', 'Rohtak': '124001', 'Hisar': '125001' }
  },
  'Himachal Pradesh': {
    cities: ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Kullu', 'Manali'],
    pincodes: { 'Shimla': '171001', 'Dharamshala': '176215', 'Solan': '173212', 'Mandi': '175001', 'Kullu': '175101', 'Manali': '175131' }
  },
  'Jharkhand': {
    cities: ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh'],
    pincodes: { 'Ranchi': '834001', 'Jamshedpur': '831001', 'Dhanbad': '826001', 'Bokaro': '827001', 'Deoghar': '814112', 'Hazaribagh': '825301' }
  },
  'Karnataka': {
    cities: ['Bangalore', 'Mysore', 'Mangalore', 'Hubli', 'Belgaum', 'Gulbarga', 'Dharwad'],
    pincodes: { 'Bangalore': '560001', 'Mysore': '570001', 'Mangalore': '575001', 'Hubli': '580001', 'Belgaum': '590001', 'Gulbarga': '585101', 'Dharwad': '580001' }
  },
  'Kerala': {
    cities: ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Kannur'],
    pincodes: { 'Thiruvananthapuram': '695001', 'Kochi': '682001', 'Kozhikode': '673001', 'Thrissur': '680001', 'Kollam': '691001', 'Kannur': '670001' }
  },
  'Madhya Pradesh': {
    cities: ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Ratlam'],
    pincodes: { 'Indore': '452001', 'Bhopal': '462001', 'Jabalpur': '482001', 'Gwalior': '474001', 'Ujjain': '456001', 'Sagar': '470001', 'Ratlam': '457001' }
  },
  'Maharashtra': {
    cities: ['Mumbai', 'Pune', 'Nagpur', 'Thane', 'Nashik', 'Aurangabad', 'Solapur'],
    pincodes: { 'Mumbai': '400001', 'Pune': '411001', 'Nagpur': '440001', 'Thane': '400601', 'Nashik': '422001', 'Aurangabad': '431001', 'Solapur': '413001' }
  },
  'Manipur': {
    cities: ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur'],
    pincodes: { 'Imphal': '795001', 'Thoubal': '795138', 'Bishnupur': '795126', 'Churachandpur': '795128' }
  },
  'Meghalaya': {
    cities: ['Shillong', 'Tura', 'Jowai', 'Nongstoin'],
    pincodes: { 'Shillong': '793001', 'Tura': '794001', 'Jowai': '793150', 'Nongstoin': '793119' }
  },
  'Mizoram': {
    cities: ['Aizawl', 'Lunglei', 'Champhai', 'Serchhip'],
    pincodes: { 'Aizawl': '796001', 'Lunglei': '796701', 'Champhai': '796321', 'Serchhip': '796181' }
  },
  'Nagaland': {
    cities: ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang'],
    pincodes: { 'Kohima': '797001', 'Dimapur': '797112', 'Mokokchung': '798601', 'Tuensang': '798612' }
  },
  'Odisha': {
    cities: ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri'],
    pincodes: { 'Bhubaneswar': '751001', 'Cuttack': '753001', 'Rourkela': '769001', 'Berhampur': '760001', 'Sambalpur': '768001', 'Puri': '752001' }
  },
  'Punjab': {
    cities: ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali'],
    pincodes: { 'Ludhiana': '141001', 'Amritsar': '143001', 'Jalandhar': '144001', 'Patiala': '147001', 'Bathinda': '151001', 'Mohali': '160055' }
  },
  'Rajasthan': {
    cities: ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Udaipur', 'Ajmer', 'Bharatpur'],
    pincodes: { 'Jaipur': '302001', 'Jodhpur': '342001', 'Kota': '324001', 'Bikaner': '334001', 'Udaipur': '313001', 'Ajmer': '305001', 'Bharatpur': '321001' }
  },
  'Sikkim': {
    cities: ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan'],
    pincodes: { 'Gangtok': '737101', 'Namchi': '737126', 'Gyalshing': '737111', 'Mangan': '737116' }
  },
  'Tamil Nadu': {
    cities: ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Vellore'],
    pincodes: { 'Chennai': '600001', 'Coimbatore': '641001', 'Madurai': '625001', 'Tiruchirappalli': '620001', 'Salem': '636001', 'Tirunelveli': '627001', 'Vellore': '632001' }
  },
  'Telangana': {
    cities: ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Mahbubnagar'],
    pincodes: { 'Hyderabad': '500001', 'Warangal': '506001', 'Nizamabad': '503001', 'Khammam': '507001', 'Karimnagar': '505001', 'Mahbubnagar': '509001' }
  },
  'Tripura': {
    cities: ['Agartala', 'Udaipur', 'Dharmanagar', 'Kailashahar'],
    pincodes: { 'Agartala': '799001', 'Udaipur': '799120', 'Dharmanagar': '799250', 'Kailashahar': '799277' }
  },
  'Uttar Pradesh': {
    cities: ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Varanasi', 'Meerut', 'Allahabad', 'Noida'],
    pincodes: { 'Lucknow': '226001', 'Kanpur': '208001', 'Ghaziabad': '201001', 'Agra': '282001', 'Varanasi': '221001', 'Meerut': '250001', 'Allahabad': '211001', 'Noida': '201301' }
  },
  'Uttarakhand': {
    cities: ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Nainital'],
    pincodes: { 'Dehradun': '248001', 'Haridwar': '249401', 'Roorkee': '247667', 'Haldwani': '263139', 'Rudrapur': '263153', 'Nainital': '263001' }
  },
  'West Bengal': {
    cities: ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Malda'],
    pincodes: { 'Kolkata': '700001', 'Howrah': '711101', 'Durgapur': '713201', 'Asansol': '713301', 'Siliguri': '734001', 'Malda': '732101' }
  },
  'Andaman and Nicobar Islands': {
    cities: ['Port Blair', 'Diglipur', 'Rangat'],
    pincodes: { 'Port Blair': '744101', 'Diglipur': '744202', 'Rangat': '744205' }
  },
  'Chandigarh': {
    cities: ['Chandigarh'],
    pincodes: { 'Chandigarh': '160001' }
  },
  'Dadra and Nagar Haveli and Daman and Diu': {
    cities: ['Daman', 'Diu', 'Silvassa'],
    pincodes: { 'Daman': '396210', 'Diu': '362520', 'Silvassa': '396230' }
  },
  'Lakshadweep': {
    cities: ['Kavaratti', 'Agatti', 'Minicoy'],
    pincodes: { 'Kavaratti': '682555', 'Agatti': '682553', 'Minicoy': '682559' }
  },
  'Delhi': {
    cities: ['New Delhi', 'North Delhi', 'South Delhi', 'East Delhi', 'West Delhi'],
    pincodes: { 'New Delhi': '110001', 'North Delhi': '110006', 'South Delhi': '110016', 'East Delhi': '110051', 'West Delhi': '110015' }
  },
  'Puducherry': {
    cities: ['Puducherry', 'Karaikal', 'Mahe', 'Yanam'],
    pincodes: { 'Puducherry': '605001', 'Karaikal': '609602', 'Mahe': '673310', 'Yanam': '533464' }
  },
  'Ladakh': {
    cities: ['Leh', 'Kargil'],
    pincodes: { 'Leh': '194101', 'Kargil': '194103' }
  },
  'Jammu and Kashmir': {
    cities: ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla', 'Udhampur'],
    pincodes: { 'Srinagar': '190001', 'Jammu': '180001', 'Anantnag': '192101', 'Baramulla': '193101', 'Udhampur': '182101' }
  }
};

// Indian Languages
const INDIAN_LANGUAGES = [
  'Telugu', 'Tamil', 'Kannada', 'Malayalam', 'Bengali',
  'Marathi', 'Gujarati', 'Punjabi', 'Odia', 'Assamese',
  'Urdu', 'Konkani', 'Manipuri', 'Sanskrit', 'Nepali',
  'Sindhi', 'Dogri', 'Kashmiri', 'Bodo', 'Maithili', 'Santhali'
];

// Searchable Dropdown Component
interface SearchableDropdownProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  disabled?: boolean;
  required?: boolean;
  isDark?: boolean;
}

function SearchableDropdown({ options, value, onChange, placeholder, disabled, required, isDark }: SearchableDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filtered = options.filter(opt =>
    opt.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none text-left flex items-center justify-between ${isDark
          ? `${disabled ? 'bg-neutral-800/50' : 'bg-neutral-800'} border-neutral-700 text-white focus:ring-2 focus:ring-neutral-600`
          : `${disabled ? 'bg-gray-100' : 'bg-white'} border-gray-300 text-gray-900 focus:ring-2 focus:ring-gray-900`
          } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
      >
        <span className={value ? '' : isDark ? 'text-neutral-500' : 'text-gray-400'}>
          {value || placeholder}
        </span>
        <svg
          className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''} ${isDark ? 'text-neutral-400' : 'text-gray-400'
            }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className={`absolute z-50 w-full mt-2 rounded-lg shadow-lg border overflow-hidden ${isDark ? 'bg-neutral-800 border-neutral-700' : 'bg-white border-gray-200'
          }`}>
          <div className={`p-3 border-b ${isDark ? 'border-neutral-700' : 'border-gray-200'}`}>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search..."
              className={`w-full px-3 py-2 rounded-lg border outline-none text-sm ${isDark
                ? 'bg-neutral-900 border-neutral-700 text-white placeholder-neutral-500'
                : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400'
                }`}
              autoFocus
            />
          </div>

          <div className="max-h-60 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className={`px-4 py-8 text-center text-sm ${isDark ? 'text-neutral-500' : 'text-gray-400'}`}>
                No results found
              </div>
            ) : (
              filtered.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => {
                    onChange(option);
                    setIsOpen(false);
                    setSearch('');
                  }}
                  className={`w-full px-4 py-2.5 text-left text-sm transition-colors flex items-center justify-between ${value === option
                    ? isDark
                      ? 'bg-neutral-700 text-white'
                      : 'bg-gray-100 text-gray-900'
                    : isDark
                      ? 'text-neutral-300 hover:bg-neutral-700'
                      : 'text-gray-700 hover:bg-gray-50'
                    }`}
                >
                  <span>{option}</span>
                  {value === option && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Date Picker Component (Improved Logic)
interface DatePickerProps {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  isDark?: boolean;
}

function DatePicker({ value, onChange, required, isDark }: DatePickerProps) {
  const [day, setDay] = useState('');
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');

  // Hydrate from initial value
  useEffect(() => {
    if (value) {
      const [y, m, d] = value.split('-');
      setYear(y);
      setMonth(m);
      setDay(d);
    }
  }, [value]);

  // Update parent when components change
  useEffect(() => {
    if (day && month && year) {
      onChange(`${year}-${month}-${day}`);
    }
  }, [day, month, year, onChange]);

  // Calculate days in the selected month/year
  const getDaysInMonth = (y: string, m: string) => {
    if (!y || !m) return 31; // Default fallback
    // Date(year, month, 0) gives the last day of the previous month
    // month is 1-indexed here, so (y, m, 0) works perfectly for determining length
    return new Date(parseInt(y), parseInt(m), 0).getDate();
  };

  const daysCount = getDaysInMonth(year, month);
  const days = Array.from({ length: daysCount }, (_, i) => String(i + 1).padStart(2, '0'));

  // Reset day if it becomes invalid (e.g. Feb 30)
  useEffect(() => {
    if (day && parseInt(day) > daysCount) {
      setDay('');
    }
  }, [daysCount, day]);

  const months = [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
  ];
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 100 }, (_, i) => String(currentYear - i));

  return (
    <div className="grid grid-cols-3 gap-3">
      <SearchableDropdown
        options={days}
        value={day}
        onChange={setDay}
        placeholder="Day"
        required={required}
        isDark={isDark}
        disabled={!month || !year} // Force Year/Month selection first
      />
      <SearchableDropdown
        options={months.map(m => m.label)}
        value={months.find(m => m.value === month)?.label || ''}
        onChange={(label) => {
          const m = months.find(mo => mo.label === label);
          if (m) setMonth(m.value);
        }}
        placeholder="Month"
        required={required}
        isDark={isDark}
      />
      <SearchableDropdown
        options={years}
        value={year}
        onChange={setYear}
        placeholder="Year"
        required={required}
        isDark={isDark}
      />
    </div>
  );
}

export default function CompleteProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [roleLocked, setRoleLocked] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Common fields
  const [fullName, setFullName] = useState('');
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState<'male' | 'female' | 'other' | ''>('');
  const [primaryLanguage, setPrimaryLanguage] = useState('');
  const [maskedAadhar, setMaskedAadhar] = useState('');
  const [phone, setPhone] = useState('');

  // Address fields
  const [country] = useState('India');
  const [state, setState] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState('');

  // Role selector
  const [role, setRole] = useState<Role>('patient');

  // Doctor fields
  const [licenseNumber, setLicenseNumber] = useState('');
  const [hospital, setHospital] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [qualifications, setQualifications] = useState('');
  const [availability, setAvailability] = useState('');

  // Operator fields
  const [organization, setOrganization] = useState('');
  const [centerLocation, setCenterLocation] = useState('');
  const [operatorContact, setOperatorContact] = useState('');

  // Patient fields
  const [medicalHistory, setMedicalHistory] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');

  const states = Object.keys(INDIA_STATES);
  // Safe access for cities
  const cities = state ? (INDIA_STATES[state]?.cities || []) : [];

  // Detect system theme
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setTheme(mediaQuery.matches ? 'dark' : 'light');

    const handler = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    (async () => {
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser();
      if (error || !user) {
        setStatus('Not authenticated. Please sign in.');
        setLoading(false);
        return;
      }
      setUserId(user.id);

      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .maybeSingle();

      if (profile) {
        setFullName(profile.full_name ?? '');
        setDob(profile.dob ?? '');
        setGender(profile.gender ?? '');
        setPrimaryLanguage(profile.primary_language ?? '');
        setMaskedAadhar(profile.masked_aadhar ?? '');
        setPhone(profile.phone ?? '');
        setState(profile.state ?? '');
        setCity(profile.city ?? '');
        setPostalCode(profile.postal_code ?? '');
        setRole(profile.role ?? 'patient');
        setRoleLocked(profile.role_locked ?? false);

        setLicenseNumber(profile.license_number ?? '');
        setHospital(profile.hospital ?? '');
        setSpecialization(profile.specialization ?? '');
        setQualifications(profile.qualifications ?? '');
        setAvailability(profile.availability ?? '');

        setOrganization(profile.organization ?? '');
        setCenterLocation(profile.center_location ?? '');
        setOperatorContact(profile.operator_contact ?? '');

        setMedicalHistory(profile.medical_history ?? '');
        setEmergencyContact(profile.emergency_contact ?? '');
      }
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    // Safe check using optional chaining to prevent crashes
    if (state && city && INDIA_STATES[state]?.pincodes) {
      setPostalCode(INDIA_STATES[state].pincodes[city] || '');
    }
  }, [city, state]);

  const validate = () => {
    if (!fullName.trim()) return 'Full name is required';
    if (!dob) return 'Date of birth is required';
    if (!gender) return 'Gender is required';
    if (!primaryLanguage) return 'Primary language is required';
    if (maskedAadhar && maskedAadhar.length !== 4) return 'Aadhar last 4 digits must be exactly 4 characters';
    if (!phone.trim()) return 'Phone number is required';
    if (!/^[6-9]\d{9}$/.test(phone)) return 'Invalid Indian phone number';
    if (!state) return 'State is required';
    if (!city) return 'City is required';
    if (!postalCode) return 'Postal code is required';

    if (role === 'doctor') {
      if (!licenseNumber.trim()) return 'License number required for doctors';
      if (!specialization.trim()) return 'Specialization required for doctors';
    }
    if (role === 'operator') {
      if (!organization.trim()) return 'Organization required for operators';
    }
    if (role === 'patient') {
      if (!emergencyContact.trim()) return 'Emergency contact required for patients';
      if (!/^[6-9]\d{9}$/.test(emergencyContact)) return 'Invalid emergency contact number';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    const err = validate();
    if (err) return setStatus(err);
    if (!userId) return setStatus('No authenticated user');

    setLoading(true);

    // Using explicit interface for Type Safety
    const payload: ProfileInsert = {
      id: userId,
      full_name: fullName.trim(),
      dob,
      gender,
      primary_language: primaryLanguage,
      masked_aadhar: maskedAadhar || null,
      phone: phone.trim(),
      country,
      state,
      city,
      postal_code: postalCode,
      role,
      role_locked: true,
      updated_at: new Date().toISOString(),
    };

    if (role === 'doctor') {
      payload.license_number = licenseNumber.trim();
      payload.hospital = hospital.trim();
      payload.specialization = specialization.trim();
      payload.qualifications = qualifications.trim();
      payload.availability = availability.trim();
    } else if (role === 'operator') {
      payload.organization = organization.trim();
      payload.center_location = centerLocation.trim();
      payload.operator_contact = operatorContact.trim();
    } else if (role === 'patient') {
      payload.medical_history = medicalHistory.trim();
      payload.emergency_contact = emergencyContact.trim();
    }

    const { error } = await supabase
      .from('profiles')
      .upsert(payload);

    setLoading(false);

    if (error) {
      setStatus(`Save error: ${error.message}`);
      return;
    }

    setShowSuccess(true);

    setTimeout(() => {
      // Redirect to the role-specific dashboard
      router.push(`/dashboard/${role}`);
    }, 2500);
  };

  const isDark = theme === 'dark';

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-black' : 'bg-white'}`}>
        <div className="flex flex-col items-center gap-4">
          <div className={`animate-spin rounded-full h-12 w-12 border-b-2 ${isDark ? 'border-white' : 'border-gray-900'
            }`}></div>
          <p className={`font-medium ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
            Loading your profile...
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={`min-h-screen py-12 px-4 transition-colors ${isDark ? 'bg-black' : 'bg-white'}`}>
        <main className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${isDark ? 'bg-neutral-900' : 'bg-gray-100'
                }`}>
                <svg className={`w-7 h-7 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
            <h1 className={`text-3xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Complete Your Profile
            </h1>
            <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
              Please fill in your details to continue
            </p>
          </div>

          {/* Form Card */}
          <div className={`rounded-2xl border p-8 ${isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200 shadow-sm'
            }`}>
            <form onSubmit={handleSubmit} className="space-y-6">

              {/* Role Selection */}
              <div className={`pb-6 border-b ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
                <label className={`block text-sm font-medium mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Select Your Role <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {(['patient', 'doctor', 'operator'] as Role[]).map((r) => (
                    <button
                      key={r}
                      type="button"
                      disabled={roleLocked}
                      onClick={() => !roleLocked && setRole(r)}
                      className={`relative p-4 rounded-lg border-2 transition-all ${role === r
                        ? isDark
                          ? 'border-white bg-neutral-800'
                          : 'border-gray-900 bg-gray-50'
                        : isDark
                          ? 'border-neutral-700 hover:border-neutral-600'
                          : 'border-gray-200 hover:border-gray-300'
                        } ${roleLocked ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <div className="flex flex-col items-center gap-2">
                        {r === 'patient' && (
                          <svg className={`w-8 h-8 ${role === r ? (isDark ? 'text-white' : 'text-gray-900') : (isDark ? 'text-neutral-500' : 'text-gray-400')}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        )}
                        {r === 'doctor' && (
                          <svg className={`w-8 h-8 ${role === r ? (isDark ? 'text-white' : 'text-gray-900') : (isDark ? 'text-neutral-500' : 'text-gray-400')}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        )}
                        {r === 'operator' && (
                          <svg className={`w-8 h-8 ${role === r ? (isDark ? 'text-white' : 'text-gray-900') : (isDark ? 'text-neutral-500' : 'text-gray-400')}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        )}
                        <span className={`text-sm font-medium capitalize ${role === r ? (isDark ? 'text-white' : 'text-gray-900') : (isDark ? 'text-neutral-400' : 'text-gray-600')
                          }`}>
                          {r}
                        </span>
                      </div>
                      {role === r && (
                        <div className="absolute top-2 right-2">
                          <svg className={`w-5 h-5 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
                {roleLocked && (
                  <p className={`text-xs mt-2 flex items-center gap-1 ${isDark ? 'text-yellow-500' : 'text-yellow-600'}`}>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                    </svg>
                    Role is locked
                  </p>
                )}
              </div>

              {/* Personal Information */}
              <div className="space-y-4">
                <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Personal Information
                </h2>

                <div className="grid md:grid-cols-2 gap-4">
                  {/* Full Name */}
                  <div className="md:col-span-2">
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Full Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                      className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                        ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                        }`}
                    />
                  </div>

                  {/* Date of Birth */}
                  <div className="md:col-span-2">
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Date of Birth <span className="text-red-500">*</span>
                    </label>
                    <DatePicker value={dob} onChange={setDob} required isDark={isDark} />
                  </div>

                  {/* Gender */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Gender <span className="text-red-500">*</span>
                    </label>
                    <SearchableDropdown
                      options={['Male', 'Female', 'Other']}
                      value={gender ? gender.charAt(0).toUpperCase() + gender.slice(1) : ''}
                      onChange={(val) => setGender(val.toLowerCase() as any)}
                      placeholder="Select Gender"
                      required
                      isDark={isDark}
                    />
                  </div>

                  {/* Primary Language (NEW FIELD) */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Primary Language <span className="text-red-500">*</span>
                    </label>
                    <SearchableDropdown
                      options={INDIAN_LANGUAGES}
                      value={primaryLanguage}
                      onChange={setPrimaryLanguage}
                      placeholder="Select Native Language"
                      required
                      isDark={isDark}
                    />
                  </div>

                  {/* Aadhar Last 4 */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Aadhar Last 4 <span className={isDark ? 'text-neutral-500' : 'text-gray-400'}>(Optional)</span>
                    </label>
                    <input
                      type="text"
                      value={maskedAadhar}
                      onChange={(e) => setMaskedAadhar(e.target.value.replace(/\D/g, '').slice(0, 4))}
                      placeholder="XXXX"
                      maxLength={4}
                      className={`w-full px-4 py-3 rounded-lg border transition-all outline-none text-center text-lg font-mono ${isDark
                        ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500'
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                        }`}
                    />
                  </div>

                  {/* Phone */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Contact Phone <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <div className={`absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none font-medium ${isDark ? 'text-neutral-400' : 'text-gray-500'
                        }`}>
                        +91
                      </div>
                      <input
                        type="tel"
                        required
                        value={phone}
                        onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                        placeholder="9876543210"
                        maxLength={10}
                        className={`w-full pl-16 pr-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Address Information */}
              <div className={`space-y-4 pt-6 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
                <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Address Information
                </h2>

                <div className="grid md:grid-cols-2 gap-4">
                  {/* Country */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      Country <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={country}
                      disabled
                      className={`w-full px-4 py-3 rounded-lg border cursor-not-allowed ${isDark
                        ? 'bg-neutral-800/50 border-neutral-700 text-neutral-400'
                        : 'bg-gray-100 border-gray-200 text-gray-600'
                        }`}
                    />
                  </div>

                  {/* State */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      State <span className="text-red-500">*</span>
                    </label>
                    <SearchableDropdown
                      options={states}
                      value={state}
                      onChange={(val) => {
                        setState(val);
                        setCity('');
                        setPostalCode('');
                      }}
                      placeholder="Select State"
                      required
                      isDark={isDark}
                    />
                  </div>

                  {/* City */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      City <span className="text-red-500">*</span>
                    </label>
                    <SearchableDropdown
                      options={cities}
                      value={city}
                      onChange={setCity}
                      placeholder="Select City"
                      disabled={!state}
                      required
                      isDark={isDark}
                    />
                  </div>

                  {/* Postal Code */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                      PIN Code <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={postalCode}
                      onChange={(e) => setPostalCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="Auto-filled"
                      maxLength={6}
                      className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                        ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                        }`}
                    />
                  </div>
                </div>
              </div>

              {/* Role-specific fields - Doctor */}
              {role === 'doctor' && (
                <div className={`space-y-4 pt-6 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
                  <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Doctor Credentials
                  </h2>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        License Number <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={licenseNumber}
                        onChange={(e) => setLicenseNumber(e.target.value)}
                        placeholder="Medical license number"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Specialization <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={specialization}
                        onChange={(e) => setSpecialization(e.target.value)}
                        placeholder="e.g., Cardiology"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Hospital / Clinic
                      </label>
                      <input
                        type="text"
                        value={hospital}
                        onChange={(e) => setHospital(e.target.value)}
                        placeholder="Hospital or clinic name"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Qualifications
                      </label>
                      <input
                        type="text"
                        value={qualifications}
                        onChange={(e) => setQualifications(e.target.value)}
                        placeholder="MBBS, MD, etc."
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Availability
                      </label>
                      <input
                        type="text"
                        value={availability}
                        onChange={(e) => setAvailability(e.target.value)}
                        placeholder="e.g., Mon-Fri 10:00-16:00"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Role-specific fields - Operator */}
              {role === 'operator' && (
                <div className={`space-y-4 pt-6 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
                  <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Operator Details
                  </h2>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Organization <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        placeholder="Organization name"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Center Location
                      </label>
                      <input
                        type="text"
                        value={centerLocation}
                        onChange={(e) => setCenterLocation(e.target.value)}
                        placeholder="Center location"
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Operator Contact
                      </label>
                      <div className="relative">
                        <div className={`absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none font-medium ${isDark ? 'text-neutral-400' : 'text-gray-500'
                          }`}>
                          +91
                        </div>
                        <input
                          type="tel"
                          value={operatorContact}
                          onChange={(e) => setOperatorContact(e.target.value.replace(/\D/g, '').slice(0, 10))}
                          placeholder="9876543210"
                          maxLength={10}
                          className={`w-full pl-16 pr-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                            ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                            : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                            }`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Role-specific fields - Patient */}
              {role === 'patient' && (
                <div className={`space-y-4 pt-6 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
                  <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    Medical Information
                  </h2>

                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Medical History
                      </label>
                      <textarea
                        value={medicalHistory}
                        onChange={(e) => setMedicalHistory(e.target.value)}
                        placeholder="Any allergies, chronic conditions, past surgeries, etc."
                        rows={4}
                        className={`w-full px-4 py-3 rounded-lg border transition-all outline-none resize-none focus:ring-2 focus:ring-offset-0 ${isDark
                          ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                          }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-neutral-300' : 'text-gray-700'}`}>
                        Emergency Contact <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <div className={`absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none font-medium ${isDark ? 'text-neutral-400' : 'text-gray-500'
                          }`}>
                          +91
                        </div>
                        <input
                          type="tel"
                          required
                          value={emergencyContact}
                          onChange={(e) => setEmergencyContact(e.target.value.replace(/\D/g, '').slice(0, 10))}
                          placeholder="9876543210 (Parent/Guardian/Relative)"
                          maxLength={10}
                          className={`w-full pl-16 pr-4 py-3 rounded-lg border transition-all outline-none focus:ring-2 focus:ring-offset-0 ${isDark
                            ? 'bg-neutral-800 border-neutral-700 text-white placeholder-neutral-500 focus:ring-neutral-600'
                            : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:ring-gray-900'
                            }`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Error Status */}
              {status && (status.includes('error') || status.includes('Invalid') || status.includes('required')) && (
                <div className={`p-3 rounded-lg text-sm ${isDark
                  ? 'bg-red-950/50 text-red-400 border border-red-900'
                  : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                  {status}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 px-6 rounded-lg font-medium transition-all disabled:opacity-50 ${isDark
                  ? 'bg-white text-black hover:bg-neutral-100'
                  : 'bg-gray-900 text-white hover:bg-gray-800'
                  }`}
              >
                {loading ? 'Saving Profile...' : 'Save & Continue'}
              </button>
            </form>
          </div>
        </main>
      </div>

      {/* Success Overlay */}
      {showSuccess && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className={`rounded-2xl p-12 shadow-xl max-w-md mx-4 ${isDark ? 'bg-neutral-900' : 'bg-white'
            }`}>
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${isDark ? 'bg-green-950' : 'bg-green-100'
                  }`}>
                  <svg className={`w-8 h-8 ${isDark ? 'text-green-400' : 'text-green-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <h2 className={`text-2xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Profile Saved!
              </h2>
              <p className={`text-sm mb-6 ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                Redirecting to your dashboard...
              </p>
              <div className={`animate-spin h-6 w-6 border-2 border-t-transparent rounded-full mx-auto ${isDark ? 'border-white' : 'border-gray-900'
                }`}></div>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');
        
        * {
          font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
      `}</style>
    </>
  );
}
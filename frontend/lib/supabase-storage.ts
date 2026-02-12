// frontend/lib/supabase-storage.ts

import supabase from './supabaseClient';

// These are the specific bucket names we created in the Supabase dashboard
// Make sure these match exactly what's in the Storage section
export const BUCKETS = {
    CT_SCANS: 'ct_scans',           // For the raw .zip or .npy files
    ML_JSON: 'ml_json',             // For findings.json from backend
    REPORTS: 'reports',             // For the generated PDFs
    CHAT_ATTACHMENTS: 'chat_attachments', // Images sent in chat
    MASKS: 'masks',                 // Nodule segmentation masks (.npy)
} as const;

export type BucketName = typeof BUCKETS[keyof typeof BUCKETS];

// Simple interface for upload results
export interface UploadResult {
    success: boolean;
    path: string | null;
    publicUrl: string | null;
    error: string | null;
}

// Interface for when we get a secure link
export interface SignedUrlResult {
    success: boolean;
    url: string | null;
    error: string | null;
}

// Helper to make a path for the file in storage. 
// We use timestamp to make sure we don't accidentally overwrite files with same name.
// Format: userId/scanId/timestamp_filename
export function generateFilePath(
    userId: string,
    scanId: string,
    filename: string
): string {
    const timestamp = Date.now();
    // basic cleanup to remove weird characters from filename
    const sanitizedFilename = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
    return `${userId}/${scanId}/${timestamp}_${sanitizedFilename}`;
}

// Simpler path generator just for scans
// Format: scanId/filename
export function generateScanPath(scanId: string, filename: string): string {
    const sanitizedFilename = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
    return `${scanId}/${sanitizedFilename}`;
}

// Main function to upload any file to a specific bucket
export async function uploadFile(
    bucket: BucketName,
    path: string,
    file: File,
    options?: {
        cacheControl?: string;
        upsert?: boolean;
        contentType?: string;
    }
): Promise<UploadResult> {
    try {
        const { data, error } = await supabase.storage
            .from(bucket)
            .upload(path, file, {
                cacheControl: options?.cacheControl || '3600',
                upsert: options?.upsert || false,
                contentType: options?.contentType || file.type,
            });

        if (error) {
            console.error('Upload error:', error);
            return {
                success: false,
                path: null,
                publicUrl: null,
                error: error.message,
            };
        }

        // Try to get a public URL just in case the bucket is public
        const { data: urlData } = supabase.storage
            .from(bucket)
            .getPublicUrl(data.path);

        return {
            success: true,
            path: data.path,
            publicUrl: urlData.publicUrl,
            error: null,
        };
    } catch (e) {
        // Catch any unexpected crashes
        const errorMessage = e instanceof Error ? e.message : 'Unknown upload error';
        console.error('Upload exception:', e);
        return {
            success: false,
            path: null,
            publicUrl: null,
            error: errorMessage,
        };
    }
}

// Wrapper specifically for uploading CT scans
// Sets a longer cache time since these files don't change
export async function uploadCTScan(
    scanId: string,
    file: File
): Promise<UploadResult> {
    const path = generateScanPath(scanId, file.name);
    return uploadFile(BUCKETS.CT_SCANS, path, file, {
        upsert: false,
        cacheControl: '86400', // 24 hours
    });
}

// Get a secure link that expires after some time (default 1 hour)
// We use this for private files like medical reports
export async function getSignedUrl(
    bucket: BucketName,
    path: string,
    expiresInSeconds: number = 3600
): Promise<SignedUrlResult> {
    try {
        const { data, error } = await supabase.storage
            .from(bucket)
            .createSignedUrl(path, expiresInSeconds);

        if (error) {
            console.error('Signed URL error:', error);
            return {
                success: false,
                url: null,
                error: error.message,
            };
        }

        return {
            success: true,
            url: data.signedUrl,
            error: null,
        };
    } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Unknown error';
        console.error('Signed URL exception:', e);
        return {
            success: false,
            url: null,
            error: errorMessage,
        };
    }
}

// Helper to get PDF links quickly
export async function getReportUrl(
    scanId: string,
    reportType: 'clinician' | 'patient',
    expiresInSeconds: number = 3600
): Promise<SignedUrlResult> {
    const filename = reportType === 'clinician'
        ? 'clinician_report.pdf'
        : 'patient_report.pdf';

    // Reports are stored in folders named by scanId
    const path = `${scanId}/${filename}`;
    return getSignedUrl(BUCKETS.REPORTS, path, expiresInSeconds);
}

// This function handles the download logic
// It fetches the file blob and then forces the browser to download it
export async function downloadFile(
    bucket: BucketName,
    path: string,
    downloadFilename?: string
): Promise<{ success: boolean; error: string | null }> {
    try {
        const { data, error } = await supabase.storage
            .from(bucket)
            .download(path);

        if (error) {
            console.error('Download error:', error);
            return { success: false, error: error.message };
        }

        // Trick to trigger download in browser
        const url = URL.createObjectURL(data);
        const a = document.createElement('a');
        a.href = url;
        // Use provided name or fallback to the file path name
        a.download = downloadFilename || path.split('/').pop() || 'download';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        return { success: true, error: null };
    } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Unknown download error';
        console.error('Download exception:', e);
        return { success: false, error: errorMessage };
    }
}

// Specific downloader for reports
export async function downloadReport(
    scanId: string,
    reportType: 'clinician' | 'patient'
): Promise<{ success: boolean; error: string | null }> {
    const filename = reportType === 'clinician'
        ? 'clinician_report.pdf'
        : 'patient_report.pdf';

    const path = `${scanId}/${filename}`;
    const downloadName = `${reportType}_report_${scanId}.pdf`;

    return downloadFile(BUCKETS.REPORTS, path, downloadName);
}

// Deletes a file. Be careful using this!
export async function deleteFile(
    bucket: BucketName,
    path: string
): Promise<{ success: boolean; error: string | null }> {
    try {
        const { error } = await supabase.storage
            .from(bucket)
            .remove([path]);

        if (error) {
            console.error('Delete error:', error);
            return { success: false, error: error.message };
        }

        return { success: true, error: null };
    } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Unknown delete error';
        console.error('Delete exception:', e);
        return { success: false, error: errorMessage };
    }
}

// Gets a list of files in a specific folder
export async function listFiles(
    bucket: BucketName,
    folderPath: string
): Promise<{ success: boolean; files: string[]; error: string | null }> {
    try {
        const { data, error } = await supabase.storage
            .from(bucket)
            .list(folderPath);

        if (error) {
            console.error('List error:', error);
            return { success: false, files: [], error: error.message };
        }

        const files = data
            .filter(item => item.name) // ignore empty items
            .map(item => `${folderPath}/${item.name}`);

        return { success: true, files, error: null };
    } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Unknown list error';
        console.error('List exception:', e);
        return { success: false, files: [], error: errorMessage };
    }
}

// Checks if a file actually exists in storage
export async function fileExists(
    bucket: BucketName,
    path: string
): Promise<boolean> {
    try {
        const folderPath = path.substring(0, path.lastIndexOf('/'));
        const fileName = path.substring(path.lastIndexOf('/') + 1);

        const { data, error } = await supabase.storage
            .from(bucket)
            .list(folderPath);

        if (error || !data) {
            return false;
        }

        // Returns true if we find a matching filename
        return data.some(item => item.name === fileName);
    } catch (e) {
        console.error('File exists check error:', e);
        return false;
    }
}

// Get details like size and type about a file
export async function getFileMetadata(
    bucket: BucketName,
    path: string
): Promise<{
    success: boolean;
    metadata: {
        name: string;
        size: number;
        type: string;
        lastModified: string;
    } | null;
    error: string | null;
}> {
    try {
        const folderPath = path.substring(0, path.lastIndexOf('/'));
        const fileName = path.substring(path.lastIndexOf('/') + 1);

        const { data, error } = await supabase.storage
            .from(bucket)
            .list(folderPath);

        if (error) {
            return { success: false, metadata: null, error: error.message };
        }

        const file = data.find(item => item.name === fileName);

        if (!file) {
            return { success: false, metadata: null, error: 'File not found' };
        }

        return {
            success: true,
            metadata: {
                name: file.name,
                size: file.metadata?.size || 0,
                type: file.metadata?.mimetype || 'application/octet-stream',
                lastModified: file.updated_at || file.created_at || '',
            },
            error: null,
        };
    } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Unknown error';
        return { success: false, metadata: null, error: errorMessage };
    }
}

// Helper to make file sizes readable (e.g. 1.5 MB instead of bytes)
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Simple check to make sure user uploaded a valid file type
export function isValidCTScanFile(file: File): boolean {
    const validExtensions = ['.zip', '.npy', '.dcm'];
    const fileName = file.name.toLowerCase();
    return validExtensions.some(ext => fileName.endsWith(ext));
}

// Extracts the .extension from a filename
export function getFileExtension(filename: string): string {
    const lastDot = filename.lastIndexOf('.');
    return lastDot !== -1 ? filename.substring(lastDot).toLowerCase() : '';
}
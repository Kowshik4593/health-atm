# Implementation Plan - Backend Inference Integration

## Status: COMPLETED

## Goal Description
Integrate the fine-tuned **Full 3D UNet model** (`unet3d_finetuned.pth`) into the backend API. This enables the system to automatically process new patient CT scans (DICOM/NPY), detect lung nodules, and generate valid `findings.json` results for the Reporting Engine.

## What Was Done

### New Files Created

#### `backend/app/services/inference_service.py` (745 lines)
- Full 3D UNet model loading (singleton pattern, GPU/CPU auto-detect)
- HU normalization and DICOM volume loading
- Sliding window inference with configurable patch size (64) and stride (48)
- Connected component extraction for nodule detection
- Per-nodule classification with risk scoring
- GradCAM XAI heatmap generation for high-risk nodules
- Complete `analyze_scan()` pipeline that produces `findings.json`

#### `backend/app/routes/upload.py`
- `POST /upload/scan` - Handles CT scan file uploads (.zip, .npy, .npz, .dcm)
- File validation, local staging, Supabase storage upload, DB record creation
- ZIP extraction for DICOM series

#### `backend/app/routes/process.py`
- `POST /process/case/{case_id}` - Triggers ML pipeline as background task
- `GET /process/status/{case_id}` - Returns processing status
- Background pipeline: inference -> findings -> Supabase upload -> reports -> status update

### Modified Files

#### `backend/app/main.py`
- Registered upload_router and process_router
- Added inference_service and upload_service to health check
- Added ai_inference, ct_scan_upload, auto_processing features

#### `backend/app/routes/cases.py`
- Added `GET /cases/{case_id}` for status polling
- Added `GET /cases/unassigned` for operator dashboard
- Fixed route ordering (fixed paths before parameterized)

#### `backend/requirements.txt`
- Added: pydicom, scipy, scikit-image, matplotlib

#### `frontend/lib/api.ts`
- Added `getPipelineStatus()` method for monitoring

#### `frontend/app/upload/page.tsx`
- Enhanced processing state with pipeline stage indicators

#### `frontend/types/index.ts`
- Extended Nodule type to include inference-generated types

## Verification Results

### Endpoint Tests (ALL PASS)
- 28 endpoints registered
- POST /upload/scan returns 422 (no file) - correct
- POST /process/case/{id} returns 404 (bad id) - correct
- GET /process/status/{id} returns 404 (bad id) - correct
- GET /cases/{id} returns 404 (bad id) - correct
- GET /health returns 200 with new features

### Inference Pipeline Test (PASS)
- Model loaded on CUDA from unet3d_finetuned.pth
- Sliding window inference completed in ~3 seconds
- findings.json generated with all required fields
- TypeScript compilation passes with no errors

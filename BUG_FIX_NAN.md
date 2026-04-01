# Bug Fix: NaN Values in JSON Response

## Issue
```
ValueError: Out of range float values are not JSON compliant: nan
```

## Root Cause
The `shortlist_sector()` agent returns a pandas DataFrame converted to dict/list, which can contain NaN (Not a Number) values. These cannot be serialized to JSON.

## Solution
Added a utility function `clean_nan_values()` in `fastapi_backend.py` that:
1. Recursively traverses all data structures (dicts, lists)
2. Replaces NaN and Inf (infinity) values with `None`
3. Allows proper JSON serialization

## Changes Made
- Added `clean_nan_values()` utility function
- Applied to `/agents/shortlist` endpoint
- Applied to `/agents/analyze-companies` endpoint

## No Agent Changes
✅ **No agents were modified** - only the backend API wrapper was updated to handle the data properly.

## How to Test
1. **Stop the backend** (Ctrl+C in the terminal)
2. **Restart the backend:**
   ```bash
   python fastapi_backend.py
   ```
3. **Test from frontend:**
   - Go to http://localhost:3000/dashboard
   - Select a sector
   - Click "Shortlist Companies"
   - Should work without errors now

## Technical Details
The function handles:
- `NaN` (Not a Number) → `None`
- `Inf` (Infinity) → `None`
- Nested dictionaries and lists
- Preserves all other data types

This is a common issue when working with pandas DataFrames and JSON APIs.

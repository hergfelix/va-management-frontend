#!/bin/bash

echo "Waiting for OCR processing to complete..."
echo

# Wait until process finishes
while ps aux | grep -q "[b]ulk_video_ocr"; do
    THUMB_COUNT=$(ls analysis_reports/bulk_video_ocr/thumbnails/ 2>/dev/null | wc -l)
    echo "$(date +%H:%M:%S) - Still running... ($THUMB_COUNT thumbnails)"
    sleep 30
done

echo
echo "✅ OCR processing complete!"
echo

# Run organization
echo "📁 Organizing results by VA..."
source venv/bin/activate
python3 scripts/organize_ocr_results.py

echo
echo "📊 Generating VA quality report..."
python3 scripts/generate_va_quality_report.py

echo
echo "🎉 ALL DONE!"
echo
echo "Check these files:"
echo "  - october_ocr_data/ (organized data by VA)"
echo "  - analysis_reports/04_VA_QUALITY_REPORT.md"

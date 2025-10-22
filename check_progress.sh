#!/bin/bash
# Quick progress checker for OCR processing

echo "=== OCR Processing Status ==="
echo

# Check if process is running
if ps aux | grep -q "[b]ulk_video_ocr"; then
    echo "✅ Process is running"
    ps aux | grep "[b]ulk_video_ocr" | awk '{print "   PID:", $2, "| CPU Time:", $10}'
else
    echo "❌ Process not running"
fi

echo

# Count thumbnails
THUMB_COUNT=$(ls analysis_reports/bulk_video_ocr/thumbnails/ 2>/dev/null | wc -l)
echo "📸 Thumbnails downloaded: $THUMB_COUNT"

# Check results file
if [ -f "analysis_reports/bulk_video_ocr/bulk_video_ocr_results.json" ]; then
    RESULT_LINES=$(wc -l < analysis_reports/bulk_video_ocr/bulk_video_ocr_results.json)
    echo "📄 Results file: $RESULT_LINES lines"
    RESULT_SIZE=$(ls -lh analysis_reports/bulk_video_ocr/bulk_video_ocr_results.json | awk '{print $5}')
    echo "📦 Results size: $RESULT_SIZE"
else
    echo "⚠️  Results file not found yet"
fi

echo
echo "=== End ===" 

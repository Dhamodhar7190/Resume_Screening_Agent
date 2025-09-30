#!/usr/bin/env python3
"""
Test script for job description file upload functionality
"""

import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_job_description_pdf():
    """Create a simple test job description PDF"""

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Add content to PDF
    c.drawString(100, 750, "Senior Python Developer")
    c.drawString(100, 720, "")
    c.drawString(100, 690, "Job Description:")
    c.drawString(100, 660, "We are looking for a Senior Python Developer to join our team.")
    c.drawString(100, 630, "")
    c.drawString(100, 600, "Requirements:")
    c.drawString(100, 570, "- 5+ years of Python development experience")
    c.drawString(100, 540, "- Experience with Django or Flask")
    c.drawString(100, 510, "- Knowledge of PostgreSQL and Redis")
    c.drawString(100, 480, "- AWS experience preferred")
    c.drawString(100, 450, "- Strong problem-solving skills")
    c.drawString(100, 420, "- Bachelor's degree in Computer Science or related field")

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def test_job_upload_endpoint():
    """Test the job description upload endpoint"""

    print("🧪 Testing job description file upload...")

    # Create test PDF
    pdf_file = create_test_job_description_pdf()

    # Prepare file for upload
    files = {
        'file': ('test_job_description.pdf', pdf_file, 'application/pdf')
    }

    # Test upload endpoint
    try:
        print("📤 Testing /upload-job-description endpoint...")
        response = requests.post(
            'http://localhost:8000/api/v1/upload/upload-job-description',
            files=files,
            params={'enhance_with_ai': True}
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"   - Filename: {result.get('filename')}")
            print(f"   - Text length: {result.get('text_length')}")
            print(f"   - Potential title: {result.get('potential_job_title')}")
            print(f"   - Preview: {result.get('text_preview', '')[:100]}...")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_job_analysis_endpoint():
    """Test the job description analysis endpoint"""

    print("\n🧪 Testing job description file analysis...")

    # Create test PDF
    pdf_file = create_test_job_description_pdf()

    # Prepare file for upload
    files = {
        'file': ('test_job_description.pdf', pdf_file, 'application/pdf')
    }

    # Test analysis endpoint
    try:
        print("📊 Testing /analyze-job-file endpoint...")
        response = requests.post(
            'http://localhost:8000/api/v1/analysis/analyze-job-file',
            files=files,
            params={'enhance_with_ai': True}
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"   - Filename: {result.get('filename')}")
            print(f"   - Extracted title: {result.get('extracted_job_title')}")
            print(f"   - Analysis status: {result.get('status')}")

            # Check if analysis contains expected fields
            analysis = result.get('analysis', {})
            if 'required_skills' in analysis:
                required_skills = analysis['required_skills']
                print(f"   - Programming languages: {required_skills.get('programming_languages', [])}")
                print(f"   - Web frameworks: {required_skills.get('web_frameworks', [])}")
                print(f"   - Databases: {required_skills.get('databases', [])}")

            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_supported_formats():
    """Test the supported formats endpoint"""

    print("\n🧪 Testing supported formats endpoint...")

    try:
        print("📋 Testing /supported-formats endpoint...")
        response = requests.get('http://localhost:8000/api/v1/upload/supported-formats')

        if response.status_code == 200:
            result = response.json()
            print("✅ Supported formats retrieved!")
            print(f"   - Formats: {result.get('supported_formats')}")
            print(f"   - Max sizes: {result.get('max_file_size_mb')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Job Description File Upload Functionality")
    print("=" * 60)

    # Install required dependency if not available
    try:
        import reportlab
    except ImportError:
        print("⚠️ Installing reportlab for PDF generation...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        import reportlab

    success_count = 0
    total_tests = 3

    # Run tests
    if test_supported_formats():
        success_count += 1

    if test_job_upload_endpoint():
        success_count += 1

    if test_job_analysis_endpoint():
        success_count += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 All tests passed! Job description file upload is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the server and try again.")